# Session 14: Architectural Refactor — Prompt Ownership, Context Store, Dependency Graph, Event-Driven Orchestrator, Provider Router & Retry/Failover

## What We Did

A full architectural overhaul of the generation pipeline based on a structured review of five problems: prompt ownership living in the wrong service, no shared project context store, missing job dependency graph, fire-and-forget orchestration, and a flat hardcoded provider setup. Four of the five were fixed in code; one (the FFmpeg render job) was consciously deferred to Phase 2.

---

## Problem → Solution Map

| # | Problem | Severity | Status |
|---|---|---|---|
| 1 | Worker builds the Flux/Veo prompt | ❌ Must Fix | ✅ Fixed |
| 2 | No Project Context Store — data repeated per shot | ⚠️ Recommended | ✅ Fixed |
| 3 | No Dependency Graph — video dispatched before image exists | ❌ Must Fix | ✅ Fixed |
| 4 | No Render Job (FFmpeg stitching) | ⚠️ Phase 2 | ⏳ Deferred |
| 5 | Orchestrator doesn't react to events — fire and forget | ⚠️ Recommended | ✅ Fixed |

---

## Code Changes

### `services/ai-engine`

#### New package: `generation/`

All generation intelligence — context loading, prompt building, provider selection, and retries — now lives here. The AI Engine is no longer a thin HTTP wrapper.

**`generation/__init__.py`**
Package marker.

**`generation/context_store.py`** *(Fix #2)*
Redis-backed Project Context Store. The orchestrator/worker calls `store_context(job_id, context)` **once** when the production plan is ready (24h TTL). Every subsequent generation job for that `job_id` calls `load_context(job_id)` to get the full `ProjectContext` from Redis — zero repetition across shots.

Helper resolvers: `resolve_character()`, `resolve_environment()`, `resolve_brand()`, `resolve_art_direction()`.

Before: every queue message embedded the full character sheets, environments, brand guide, and art direction — repeated 50+ times for a 60-shot video.

After: one Redis key per job, referenced by every shot.

**`generation/prompt_builder.py`** *(Fix #1)*
Owns all prompt construction. Accepts a thin job descriptor (with `base_prompt` + `references`), loads the `ProjectContext`, resolves character/environment/brand/art direction, and assembles the final Flux/Veo prompt string.

- `build_image_prompt(job)` → enriched payload with `prompt`, `negative_prompt`, `_resolved` context
- `build_video_prompt(job)` → same + appends `camera_motion` directive

Switching Flux → GPT Image → Imagen requires changing the adapter only — the prompt assembly logic and the worker are untouched.

**`generation/provider_router.py`**
Static `PROVIDER_REGISTRY` of 11 providers annotated with:
- `asset_types` — which asset types this provider handles
- `strategies` — `fast | quality | cheap | auto`
- `cost_tier` — `low | medium | high`
- `quality_tier` — `standard | high | ultra`
- `adapter_fn` — factory for the real adapter callable

Providers registered:
- Image: Flux Schnell, Flux Pro, GPT Image, Imagen, SDXL
- Video: Veo 3, Runway Gen-4, Kling
- Audio: ElevenLabs (voice), Suno (music), ElevenLabs SFX

`select_provider(asset_type, strategy, preferred_name)` picks the best match. Adding a new model = one dict in the registry; nothing in the Worker or Orchestrator changes.

**`generation/scheduler.py`** *(Retry & Failover)*
Sits between the pipeline and the provider router. Implements a two-level failure model:

```
attempt 1..N  →  Provider A  (exponential backoff)
   exhausted  →  failover
attempt 1..N  →  Provider B
   exhausted  →  failover
   ...
   all failed →  ProviderExhaustedError
```

Retry config — all tunable per-job via payload fields, no code change needed:

| Field | Default | Meaning |
|---|---|---|
| `retry_limit` | `3` | Attempts per provider |
| `retry_delay_s` | `1.0 s` | First backoff wait |
| `retry_backoff` | `2.0×` | Multiplier each retry (1 → 2 → 4 s) |
| `retry_max_delay` | `30 s` | Backoff ceiling |

`ProviderExhaustedError` carries a structured attempt log:
```
All providers exhausted for asset_type='image'.
Attempt log: Flux Pro x3 (TimeoutError); GPT Image x3 (RateLimitError)
```

**`generation/pipeline.py`** *(Fix #1 + Scheduler wiring)*
The thin entry-point that wires:  
`prompt_builder` → `scheduler` → `provider_router` → `adapter`

- `run_image_pipeline(job)` 
- `run_video_pipeline(job)`
- `run_audio_pipeline(job, audio_type)`

**`config/settings.py`**
Added `REDIS_URL: str = "redis://localhost:6379"` so the context store can connect without hardcoding.

**`server.py`**
- Routed all `/generate/{queue}` requests through the new `generation.pipeline` (Fix #1) instead of calling adapters directly.
- Added `POST /api/v1/store-context` endpoint (Fix #2) — called once per job by the orchestrator.
- Added `ProviderExhaustedError` catch → HTTP 503 (distinct from HTTP 500 for context-store failures) so the worker can `nack` intelligently.

---

### `services/orchestrator`

**`src/lib/dep_graph.ts`** *(Fix #3)*
Redis-backed dependency graph. Each blocked job is stored as a single rich JSON state document:

```json
{
  "job":        "video_001",
  "queue":      "video-generation",
  "depends_on": ["image_001", "voice_001"],
  "remaining":  1,
  "status":     "WAITING"
}
```

`depends_on` is immutable (shows the original full graph). `remaining` is a live counter. `status` transitions: `WAITING` → `DISPATCHED`.

Previous approach used two separate Redis keys (a bare SET + a detached payload blob) — no status field, required `SCARD` to check remaining deps, impossible to inspect at a glance.

Functions:
- `registerJobDependency(redis, parentJobId, jobId, queue, dependsOn, payload)`
- `markDependencySatisfied(redis, parentJobId, completedJobId, registeredJobIds)` → returns `{ queue, payload }[]` for every newly unblocked job
- `getDepState(redis, parentJobId, jobId)` → reads current state for dashboards/retries

**`src/workflows/video_ad_workflow.ts`** *(renamed from `youtube-video.ts`)*
Renamed because the workflow is format-agnostic (YouTube, TikTok, Reels, CTV, etc.). The old name leaked an irrelevant platform detail into shared infrastructure.

Changes:
- All log prefixes updated to `[VideoAdWorkflow]`
- Exported functions renamed: `executeVideoAdWorkflow()` / `dispatchAssetGeneration()`
- **Fix #2**: calls `POST /api/v1/store-context` once before dispatching shots
- **Fix #3**: image jobs dispatch immediately; video jobs are held in the dependency graph until their upstream images complete
- **Fix #5**: subscribes to `job.<parentId>.asset-completed` on Redis Pub/Sub; on each event, calls `markDependencySatisfied` and dispatches any newly-unblocked jobs. Cleans up subscriptions when the pending-asset counter reaches zero.
- Job descriptors now carry `base_prompt` + `references` (thin) instead of a pre-built full prompt; also carry `strategy` and `preferred_provider` for the AI Engine's scheduler.

**`src/index.ts`**
- Import updated from `youtube-video` → `video_ad_workflow`
- Function call updated to `executeVideoAdWorkflow()`
- Type check broadened: now accepts `job.type === 'video_ad'` alongside legacy `'youtube_video'`

**`src/ingest.ts`** *(the manual ingest script)*
- Added `storeProjectContext()` — real HTTP call to `POST /api/v1/store-context` instead of the previous `console.log("Stored to Redis (Mock)")` comment
- Job payloads now include `job_id_parent` and `base_prompt` fields for Fix #1 compatibility

**`src/workflows/youtube-video.ts`** — **deleted**

---

### `services/worker`

**`src/workers/generic.worker.ts`**
- **Fix #1**: Worker no longer builds the final prompt. Forwards the thin job descriptor (with `base_prompt` + `references`) directly to the AI Engine.
- **Fix #3 + #5**: After every successful generation, publishes `job.<parentId>.asset-completed` on Redis Pub/Sub so the orchestrator can unblock dependent jobs.
- `asset-prompt` event now logs `base_prompt` (the raw scene intent) rather than a fabricated full prompt.

---

## Architecture: Before vs After

**Before (prompt ownership)**
```
CreativePlan → Orchestrator → build full prompt → RabbitMQ → Worker → AI Engine → Flux
```

**After (prompt ownership)**
```
Worker → thin descriptor (base_prompt + references) → AI Engine
                                                           │
                                          load ProjectContext (Redis)
                                          resolve Character
                                          resolve Environment
                                          resolve Brand / Art Direction
                                          build final prompt
                                          scheduler → provider_router → Flux/Veo/Imagen
```

**Before (dependency graph)**
```
for shot in shots:
    dispatch image_job   ← fires
    dispatch video_job   ← fires immediately, Veo has no image yet
```

**After (dependency graph)**
```
image_job  →  dispatched immediately
video_job  →  held in dep graph (status=WAITING, remaining=1)

image.completed event
    ↓
Orchestrator reacts (Fix #5)
    ↓
markDependencySatisfied → remaining=0, status=DISPATCHED
    ↓
video_job dispatched   ← now has the real image URL
```

---

## Key Design Decisions

**Rich dep state vs bare Redis SET**  
Storing `{ job, queue, depends_on, remaining, status }` as one JSON document (vs two separate Redis keys with a SET + payload blob) was chosen for debuggability: `redis-cli GET job:<p>:dep:<j>` shows the full state in one call. `depends_on` is immutable so you can always see the original graph, not just what's left.

**Failover chain built from registry order**  
The scheduler builds its failover list from `PROVIDER_REGISTRY` filtered by `asset_type + strategy`, with the initially selected provider first. No separate "fallback list" to maintain — adding a new provider to the registry automatically makes it a failover candidate.

**HTTP 503 for exhausted providers**  
`ProviderExhaustedError` is surfaced as 503 (Service Unavailable) rather than 500, so the worker's `nack` can be handled differently from a context-store or pipeline error. Dead-letter queue routing can key off the status code.

**`strategy` + `preferred_provider` as job-level fields**  
Rather than a global config flag, per-shot strategy hints let the orchestrator request `quality` for hero shots and `fast` or `cheap` for B-roll in the same job without any code change.

---

## Files Created / Modified This Session

| File | Action |
|---|---|
| `services/ai-engine/generation/__init__.py` | Created |
| `services/ai-engine/generation/context_store.py` | Created |
| `services/ai-engine/generation/prompt_builder.py` | Created |
| `services/ai-engine/generation/provider_router.py` | Created |
| `services/ai-engine/generation/scheduler.py` | Created (then rewritten with retry/failover) |
| `services/ai-engine/generation/pipeline.py` | Created (then updated to route through scheduler) |
| `services/ai-engine/server.py` | Rewritten |
| `services/ai-engine/config/settings.py` | Added `REDIS_URL` |
| `services/orchestrator/src/lib/dep_graph.ts` | Created (then rewritten with rich state doc) |
| `services/orchestrator/src/workflows/video_ad_workflow.ts` | Created (replaces youtube-video.ts) |
| `services/orchestrator/src/workflows/youtube-video.ts` | **Deleted** |
| `services/orchestrator/src/index.ts` | Updated imports + dispatch call |
| `services/orchestrator/src/ingest.ts` | Updated to call real store-context + thin payloads |
| `services/worker/src/workers/generic.worker.ts` | Rewritten (thin descriptor + asset-completed events) |

---

## Next Steps for Session 15

- Wire real provider adapters (Flux API, Veo API) into `adapters/image.py` and `adapters/video.py` to replace the `picsum.photos` / sample-video placeholders.
- Add a `GET /api/v1/dep-state/:jobId/:depJobId` debug endpoint on the AI Engine (or orchestrator) so the dependency graph can be inspected via the admin console.
- Consider budget-enforcement in the scheduler: check a monthly-spend Redis counter before selecting a provider, downgrade strategy when over threshold.
- Force-test the real clarification round-trip (a prompt tuned to trigger `importance_scorer` to ask a question) — still unverified live per Session 13's follow-up note.
