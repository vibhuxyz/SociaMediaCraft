# Session 12: Full Project Audit — State of the Union

## What We Did
Read every planning doc (`TODO.md`, `roadmap.md`, `docs/PROJECT_ROADMAP.md`, `ARCHITECTURE.md`, `MENTOR_MODE.md`, `LEARNING_LOG.md`, `DECISIONS.md`, `LANGGRAPH_GUIDE.md`, all `SESSION_01`–`11` files) and then audited every service (`services/ai-engine`, `services/api-gateway`, `services/orchestrator`, `services/worker`), every app (`apps/web`, `apps/admin`), and the shared `packages/*` workspace against what the docs claim exists. This is a status check, not a build session — no code was changed.

---

## Headline Finding

**V3 (the Python AI Director Brain) is real, deep, and mostly works. Everything around it — the Node.js services and the frontend — is still V0/V1-era prototype scaffolding that was never upgraded to talk to V3.** TODO.md is honest about this: V4 ("Full-Stack Integration") is the one unchecked, un-started future phase, and that gap is bigger and more scattered than the TODO line suggests.

The result today: a user typing a prompt into `apps/web` gets a real LLM-planned `CreativePlan.json` back over SSE for one code path (`DashboardPage` → `worker/planning.worker.ts` → `ai-engine`), and everything past that point — auth, credits, persistence, real asset generation, human-in-the-loop clarification — is either mocked, dead code, or missing entirely.

---

## 1. `services/ai-engine` (Python / LangGraph) — the strongest part of the codebase

**What's good:** ~30 agent nodes, a consistent `run_structured_agent` helper used by 31/38 node files, a working (in `cli.py`) interrupt/resume HITL flow, a knowledge-file loading system, and a real production plan builder.

**What's bad / broken:**
- **HITL is disabled in production.** `server.py` calls `build_graph(interrupt_after_clarification=False)` — the pause-for-clarification feature that works in `cli.py` (`interrupt_after_clarification=True`) is switched off for the actual server. The "resume" branch in `server.py` is dead code: a comment admits the answer-merging logic isn't implemented, ending in a bare `pass`.
- **Two conditional-routing functions are dead code.** `route_after_clarification` in `workflow/router.py` always returns the same node — the `{END: ...}` branch passed to `add_conditional_edges` can never fire. `route_after_classifier` (the documented Commercial-vs-Story-Film split) is defined but never wired into `graph.py` at all; the graph hardcodes everyone into `missing_info_detector_node`.
- **Model routing has holes.** `agents/common.py:534` and `agents/prompt_engineering/node.py:64` hardcode `gpt-4o-mini`/`gpt-4o` instead of using the configured free-tier OpenRouter routing — these calls will fail (or quietly bill a real OpenAI key) and directly undercut the Session 11 move to free models.
- **No persistence for checkpointing.** `MemorySaver()` is in-process only — a restart or a second worker process loses every paused conversation. There's no Postgres/Redis-backed checkpointer despite that being the whole point of HITL.
- **Unbounded in-memory cache** in `knowledge_selector/node.py` (no TTL/eviction — grows for the life of the process and never picks up file changes without a restart).
- **Dependency risk:** `litellm`, `langgraph`, `langchain-core` are unpinned in `requirements.txt` while everything else is pinned to exact (and old — `openai==1.3.5`, `anthropic==0.7.1`) versions. These are the fastest-moving dependencies in the stack and the ones most likely to break a working pipeline on a fresh install.
- **Zero automated tests.** No `pytest`, no `tests/` directory — just three manual smoke-test scripts at the repo root (`test_openrouter.py`, `test_litellm.py`, `test_incremental.py`) with `print()` instead of assertions, for a 30-node graph.
- Minor: bare `print()` used for logging in 8+ node files instead of the `logging` module already set up in `server.py`; `production_plan_builder/node.py` imports `json`/`os` for a "write to file" step that's never actually called (vestigial).

### Provider / router strategy — clarified

`providers/llm/universal_provider.py` already wraps LiteLLM, and LiteLLM *is* a universal router: the `model` string's prefix (`openrouter/...`, `openai/...`, `anthropic/...`, `gemini/...`) picks the backend, and `config/settings.py` already declares separate keys for OpenAI, Anthropic, Gemini, OpenRouter, plus a generic `CUSTOM_API_KEY`/`CUSTOM_API_BASE` pair that works as an escape hatch for any other OpenAI-compatible aggregator (Fireworks, Together, Groq, Requesty, Portkey, a self-hosted endpoint, etc.) without needing per-provider SDKs. **This is the right shape already — one router, many backends, all reachable through the same call.** Adding a second, separate router library on top would just create a second place for config to drift; the fix needed isn't architecture, it's closing the spots where code currently bypasses this single path:

- `agents/common.py:534` hardcodes `model="gpt-4o-mini"` for the validation call instead of reading `settings.MODEL_AGENT_VALIDATOR` — this ignores whatever provider/router is actually configured.
- `agents/prompt_engineering/node.py:64` calls `litellm.acompletion(model="gpt-4o", ...)` directly (imported straight from `litellm`, not through `llm_providers`/`run_structured_agent`), skipping both `settings.model_for_agent()` and the `custom_base`/`custom_key` override entirely.
- **New gap:** `GEMINI_API_KEY` is declared in `settings.py` but `dependencies.py` never passes it into `UniversalLLMProvider.__init__` or exports it to `os.environ` — a `gemini/...` model string would silently fail auth even though the key field exists and may be set in `.env`.

Fixing these three closes the loop: every agent call — whichever provider or router it targets — goes through `run_structured_agent` → `llm_providers` → LiteLLM, with no hardcoded bypasses.

---

## 2. `services/api-gateway`, `services/orchestrator`, `services/worker` (Node.js) — thin prototype, large gap vs. the architecture doc

- **No auth, credits, validation, or rate-limiting anywhere**, despite `docs/ARCHITECTURE.md` drawing all four as API Gateway responsibilities. `api-gateway/src/index.ts` has only `cors()` + `express.json()`. The `User` Prisma model has no password/role/credits fields — this was never started, not just incomplete. `zod` is a dependency but unused; `/api/plan` only checks that `prompt` is truthy. `src/server.ts` is an empty dead file.
- **No `Project` model at all.** The architecture doc's "Project Service" (Projects/Jobs/Status in Postgres) doesn't exist — the Prisma schema (`packages/database/prisma/schema.prisma`) only has bare `Job` and `User` tables, no relation between them, no `/projects` REST resource anywhere.
- **Orchestrator doesn't orchestrate.** `src/index.ts` is an if/else with one branch (`youtube_video` or fallback). A comment in `src/workflows/youtube-video.ts` admits: *"In a real Orchestrator (like Temporal/BullMQ), we would wait here... For now, we just dispatch the first step."* Failed jobs are `nack`'d and discarded, not retried. A well-built ~285-line job/EDL builder (`src/jobs/builder.ts`) exists but is never called from the running service — only from a disconnected manual script (`src/ingest.ts`, which itself fakes "Storing Context to Redis" with a `console.log`).
- **Worker only really wires up the planning stage.** `worker/src/lib/python.ts` does make a genuine HTTP call to the AI engine for plan generation (with a hacky hardcoded endpoint-rewrite for an API version mismatch) — but everything downstream of that is mocked: `generic.worker.ts`'s image/video/voice/music/sfx consumers sleep 1s, randomly fail 10%, and return fake `mock-s3-bucket` URLs; `planning.worker.ts` fakes the rest of the render pipeline with a `setInterval` and hardcoded public sample videos (BigBuckBunny, Sintel, etc.); `lib/s3.ts`'s upload/download functions are `setTimeout` stubs that never touch the real S3 client defined next to them.
- **Hardcoded default credentials in source**, not just `.env`: `minioadmin`/`minioadmin` and `amqp://user:password@localhost:5672` appear as fallback defaults baked into `api-gateway/src/index.ts` and `worker/src/lib/s3.ts` and repeated across 4 files. Low risk locally, but a landmine if this pattern reaches a shared/staging environment.
- Pervasive `any` typing on job payloads and RabbitMQ messages across all three services; no tests anywhere (no `*.test.*`, no runner configured).

---

## 3. `apps/web` (frontend) — six disconnected prototypes, not one product flow

- There is no `POST /projects` / `/analyze` / `/finalize` flow anywhere — the documented Create → Analyze → Clarify → Generate journey doesn't exist as a single flow. Instead there are **six separate, non-chained pages**: the main `DashboardPage` plus five `/admin/v0` … `/admin/v4` test consoles, each poking at one isolated backend concern.
- `DashboardPage` is the most advanced piece: it posts a prompt, opens SSE, and does parse dynamic clarification Q&A out of the AI response (genuinely more than a hardcoded form) — but it's a single free-text box, not a persisted, multi-project experience. There is no "my projects" list anywhere; nothing is durable across a page reload.
- **Most of the `/admin/v*` pages are mock-data demos wearing a "backend test" costume**: `v1.ts`, `v3.ts`, `v4.ts` call relative paths with no Vite proxy configured (would 404), and all silently fall back to `setTimeout` mock data in their `catch` blocks.
- Hardcoded, inconsistent `localhost` ports scattered through the code (`8080` for `/api/plan`, `6001` for an SSE "notification service" not in any architecture doc, `3001` for uploads) — nothing reads from a shared config/env.
- A real navigation bug: `PageLayout.tsx` links to `/v0`…`/v4`, but the router actually mounts these under `/admin/v0`…`/admin/v4` — sidebar nav in the admin console is broken.
- `apps/admin/` (the actual top-level app, distinct from the `/admin` route inside `apps/web`) is a fully empty directory — dead placeholder from the monorepo scaffold, and its name collides confusingly with the unrelated `/admin` dev-console route.
- No state management library anywhere (every page hand-rolls its own `useState` for loading/error), some `any` typing, two files of confirmed dead code (`hooks/useFetch.ts`, `components/ui/card.tsx`), no design consistency between the dark "product" theme and the light "admin" theme, and zero tests.

---

## 4. Monorepo-level gaps

- **`packages/shared`, `packages/multimodal`, `packages/tools` are entirely empty** — just subdirectory scaffolding (`config/`, `errors/`, `events/`, `logger/`, `utils/` under `shared`; `ffmpeg/`, `rabbitmq/`, `redis/`, `s3/` under `tools`) with zero files inside any of them, and nothing in any service imports `@videocraft/shared`, `@videocraft/multimodal`, or `@videocraft/tools`. This is the intended cross-service infrastructure layer (shared logger, error types, event contracts, ffmpeg/S3/Redis/RabbitMQ wrappers) and none of it has been built — every service currently reimplements its own ad-hoc version of these instead (explaining the duplicated hardcoded credentials and `any`-typed event payloads noted above).
- Root `package.json`'s `dev` script's `concurrently` names (`-n "api,worker"`) don't match the three services it actually runs (`api-gateway`, `worker`, `orchestrator`) — cosmetic but confusing in terminal output. It also doesn't start `services/ai-engine` (Python) — you have to boot that separately.
- `docs/session/SESSION_08.md` is missing from the sequence (01–06 live in `docs/session/`, 07/09/10/11 live directly in `docs/`) — a small doc-hygiene gap, not a code issue.

---

## Priority Punch List (what to build next)

1. **Wire the AI engine's HITL into the server.** Turn on `interrupt_after_clarification`, implement the answer-merge that's currently a `pass`, and back the checkpointer with Postgres/Redis instead of `MemorySaver()`. This is the single highest-leverage fix — without it, no multi-turn clarification flow can ever reach a real user.
2. **Decide the real architecture for asset generation and stop mocking it.** `worker`'s generic consumers and S3 calls are 100% fake; either build the real image/video/voice/music dispatch (V5 in TODO.md) or explicitly scope it out of the current milestone so it stops looking done.
3. **Build the actual Project Service + auth/credits layer**, or remove those boxes from `docs/ARCHITECTURE.md` until they're real — right now the docs describe a service that doesn't exist.
4. **Consolidate the frontend onto one real flow** (`Create → Analyze → Clarify → Generate`, backed by a persisted project list) and delete or clearly label the `/admin/v0-v4` mock consoles as throwaway scratch work, not product surface.
5. **Populate or delete `packages/shared` / `multimodal` / `tools`.** Every service is currently reinventing logging, error shapes, and infra clients ad hoc — this is the root cause of the repeated hardcoded credentials and inconsistent `any` typing found in every service.
6. **Pin `litellm`/`langgraph`/`langchain-core`** and add even minimal `pytest` coverage for the graph's routing logic — the two dead conditional-edge functions found in this audit would have been caught by one test each.
7. Fix the two genuinely broken things found: the `/admin` nav-path mismatch in the frontend, and the hardcoded `gpt-4o`/`gpt-4o-mini` calls in `agents/common.py` and `prompt_engineering/node.py` that bypass free-model routing.

## Next Steps for Session 13
Pick one item from the punch list above — HITL wiring (#1) is the natural next build session since it directly continues the "Human-in-the-Loop" line already open (unchecked) in `TODO.md`.
