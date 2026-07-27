# Session 13: Real End-to-End Test Pipeline (Prompt → Clarification → Plan → Mock Asset Generation)

## What We Did
Following the full-project audit in `docs/SESSION_12.md`, this session closed the biggest gap it found: the Python `ai-engine` worked in isolation, but nothing wired it to the Node services or the frontend into one real, testable loop. We implemented and **verified live** (real OpenAI calls, real service boot) a working path: prompt → real clarification pause/resume → plan → orchestrator-dispatched mock image/video generation, streamed to the UI over Redis → SSE.

Full plan is saved at `/Users/vibhu/.claude/plans/vast-singing-cloud.md`.

## Code Changes

### `services/ai-engine`
- `server.py`: flipped `build_graph(interrupt_after_clarification=True)` (was hardcoded `False`, so HITL never actually paused). Replaced the dead `if state_snapshot.next: pass` logic with a real resume path mirroring `cli.py`'s proven pattern (`update_state` + `ainvoke(None, config)`). `GeneratePlanRequest.thread_id` is now required (was defaulting to `"default"` — every job shared one graph thread) and gained `clarification_answers: dict[str, str] | None`. Added an auto-resume branch for the case where `interrupt_after` fires but `clarification_questions` came back empty (LangGraph pauses unconditionally after the node, regardless of its output — without this, "nothing to ask" jobs would dead-end).
- `adapters/image.py`, `video.py`, `audio.py`: added `asyncio.sleep(2-4s)` to simulate real generation latency.
- `adapters/image.py`, `video.py`: swapped the dead `https://mock-s3-bucket/...` URLs for real, viewable placeholders — `picsum.photos/seed/{job_id}/...` for images, a rotation of 3 public sample clips (Google's GTV bucket) for video — both marked `TODO` for the eventual real provider swap.
- `config/settings.py`: temporarily pinned `AI_ENGINE_MODEL`/`FAST_MODEL`/`SMART_MODEL`/`VALIDATOR_MODEL` to OpenAI (`gpt-4o-mini`/`gpt-4o`) since OpenRouter's free tier wasn't working; noted as a revert-later switch.

### `services/worker`
- New `lib/rabbitmq.ts` (publisher connection, mirrors orchestrator's existing helper).
- `lib/redis.ts`: widened `publishEvent`'s type union with `'awaiting-clarification'` and `'asset-prompt'`; added `decrPendingAssetCount`.
- `planning.worker.ts`: rewritten — passes `thread_id`/`clarification_answers`, fixed a real pre-existing bug (it read `aiResponse.result.x` but the ai-engine returns the plan unwrapped, no `.result` wrapper), publishes `'awaiting-clarification'` and sets `AWAITING_CLARIFICATION` status when questions come back, and — once a real plan exists — hands off to a new `plan_ready_queue` instead of the old local `setInterval` fake pipeline (which fabricated progress and hardcoded YouTube sample videos; deleted entirely).
- `generic.worker.ts`: replaced the fully-fake `sendToAIEngine` (1s timeout, 10% random failure, fake URL, no Redis events at all) with a real call to the ai-engine's already-existing-but-unused `/generate/{queue}` endpoint. Now publishes `'asset-prompt'` (the raw prompt, before generation) then `'asset-generated'` (the resulting asset) per shot, and decrements the pending-asset counter to know when the whole job is done.
- `lib/python.ts`: removed the `/api/v2/generate-plan` → `/api/v1/generate-plan` rewrite hack (worker now calls the real route directly).

### `services/orchestrator`
- New `lib/redis.ts` (same `job.{jobId}.{type}` channel convention as worker's; a `setPendingAssetCount` helper).
- `workflows/youtube-video.ts`: added `dispatchAssetGeneration(jobId, productionPlan)` — walks `prompt_pack.scenes[].shots[].{images,videos}`, sets the Redis pending count, and dispatches one real job per shot-asset to `image-generation`/`video-generation`. Publishes `'completed'` directly if a plan has zero renderable shots.
- `index.ts`: now also consumes the new `plan_ready_queue`, calling `dispatchAssetGeneration` on each message — this is the piece that makes the orchestrator actually "take the plan and send it to the ai-engine for image/video generation," per the original ask.

### `services/api-gateway`
- New `POST /api/jobs/:id/answer`: validates the job is `AWAITING_CLARIFICATION`, publishes a resume message (`{ id, prompt, resume: true, answers }`) straight to `planning_queue`.

### `apps/web`
- `DashboardPage.tsx`: tracks `jobId`; added a dedicated `'awaiting-clarification'` SSE branch (keeps the connection open, unlike the old behavior which closed it and overloaded `'completed'` for this); `handleAnswerSubmit` now POSTs to the new answer endpoint instead of starting a whole new job; added `'asset-prompt'` handling with a small "Now rendering: ..." banner; fixed the "Live Asset Generation Feed" grid, which was rendering every asset (including videos) through an `<img>` tag — it now renders `<video>` for video-type assets.

## Bugs Found & Fixed Along the Way
- `worker/lib/rabbitmq.ts`'s new file hit the same pre-existing `@types/amqplib` type mismatch documented in `SESSION_12.md` — but unlike `orchestrator` (which uses `tsx`, transpile-only, so it silently ignores the type error), `worker` uses `ts-node-dev`, which actually enforces type-checking and refused to boot. Fixed with an `any` cast, matching the workaround already used elsewhere in this codebase for the same issue.
- Found and killed a stray orphaned `ts-node-dev` process squatting on port 8080 from an earlier run, which blocked the fresh boot.

## Live Verification (not just typecheck — actually ran it)
Booted the full stack (docker compose: Postgres/RabbitMQ/Redis/MinIO; `ai-engine` via uvicorn; `bun run dev` for api-gateway/worker/orchestrator; `vite` for the frontend) and ran 3 real prompts through `POST /api/plan` with real OpenAI calls (not mocked):
- Confirmed the full chain fires exactly as designed: `api-gateway → orchestrator_queue → orchestrator → planning_queue → worker → ai-engine (real ~30-agent LangGraph run, ~35 API calls / ~2 min / ~$0.08 per run) → plan_ready_queue → orchestrator dispatches real per-shot jobs → generic workers hit the real `/generate/{queue}` endpoint → Redis → SSE`.
- Confirmed the exact live SSE event sequence: `progress` → (`asset-prompt` → `asset-generated`) × N shots → `completed`, with real prompt text and real placeholder image/video URLs.
- Confirmed the interrupt/auto-resume logic engaged correctly on every run (log: `[thread=<job-id>] No clarification needed, auto-resuming`), using each job's own `thread_id` rather than the old shared `"default"`.
- None of the 3 test prompts (including one crafted to omit a brand name) actually triggered a real clarification question — the `clarification_agent`/`importance_scorer` chose to infer sensible defaults each time. This means the pause→answer→resume *code path* is proven correct by construction (mirrors `cli.py`'s working pattern, and the auto-resume branch is confirmed firing live) but the *live "user answers a real question" round-trip* hasn't been observed yet — would need a prompt/tuning change to force it, or manual testing via the UI.

## Follow-up Discussed (Not Yet Built)
Talked through, but did not implement, a job cancellation ("Stop" button) design:
- Persist `jobId` to `localStorage` so a page refresh can reconnect to an in-flight job instead of losing it.
- A `CANCELLED` terminal status + a shared "check before processing" guard in every queue consumer (rather than trying to delete specific messages out of RabbitMQ, which isn't practical).
- A Redis `job:{jobId}:cancelled` flag checked once, cheaply, inside `run_structured_agent` in `agents/common.py` — since nearly all 30 agents already funnel through it, this gives near-hard-cancel behavior (stops future agent calls) without threading cancellation through every node file individually.
- Guard both ends of the race (check-before-start and check-before-writing-final-result) so a message that slips through mid-cancel can't overwrite a cancelled job back into a "completed" state.
- One uniform `'cancelled'` SSE event regardless of which stage the job was cancelled from, so the frontend needs exactly one handler instead of three.

## Next Steps for Session 14
Build the cancellation feature above, or force-test the real clarification round-trip (a prompt/tuning change to make `importance_scorer` ask a question), or revert `config/settings.py`'s model pins back to OpenRouter once that's working again.
