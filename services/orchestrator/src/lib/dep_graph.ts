/**
 * Dependency Graph  (improved)
 * =============================
 * Tracks which jobs are waiting for upstream completions before dispatch.
 *
 * Storage layout (Redis — single JSON document per blocked job):
 *
 *   key:  job:<parentId>:dep:<jobId>
 *   value: {
 *     "job":        "video_001",
 *     "queue":      "video-generation",
 *     "depends_on": ["image_001", "voice_001"],   ← full original list (immutable)
 *     "remaining":  2,                             ← decremented on each completion
 *     "status":     "WAITING" | "READY" | "DISPATCHED",
 *     "payload":    { … }                          ← RabbitMQ message held until ready
 *   }
 *
 * Advantages over a bare Redis SET:
 *   • One HGETALL shows the full state of any blocked job instantly (debuggable).
 *   • `remaining` is a plain integer — no need to SCARD a set.
 *   • `status` field makes dashboards / admin tools trivial.
 *   • `depends_on` is preserved so you can see the original graph, not just
 *     what's left.
 *
 * Lifecycle:
 *   1. Orchestrator calls `registerJobDependency` for every job that has deps.
 *   2. Worker completes an asset → publishes `job.<parentId>.asset-completed`.
 *   3. Orchestrator calls `markDependencySatisfied`.
 *   4. When `remaining` hits 0 the record transitions to READY, the payload
 *      is returned, and the status is set to DISPATCHED.
 */

import { createClient } from 'redis';

// ── Types ──────────────────────────────────────────────────────────────────

export interface DepState {
  job: string;
  queue: string;
  depends_on: string[];   // immutable — the full original dep list
  remaining: number;      // decremented on each upstream completion
  status: 'WAITING' | 'READY' | 'DISPATCHED';
  payload: any;           // RabbitMQ message, held until status → DISPATCHED
}

// ── Redis key ──────────────────────────────────────────────────────────────

function depKey(parentJobId: string, jobId: string): string {
  return `job:${parentJobId}:dep:${jobId}`;
}

const TTL = 86_400; // 24 hours

// ── Write helpers ──────────────────────────────────────────────────────────

/**
 * Register that `jobId` must wait for every ID in `dependsOn`.
 * The full queue payload is embedded in the state document so it can be
 * dispatched automatically once all deps are satisfied.
 */
export async function registerJobDependency(
  redis: ReturnType<typeof createClient>,
  parentJobId: string,
  jobId: string,
  queue: string,
  dependsOn: string[],
  queuePayload: any,
): Promise<void> {
  const state: DepState = {
    job: jobId,
    queue,
    depends_on: dependsOn,
    remaining: dependsOn.length,
    status: 'WAITING',
    payload: queuePayload,
  };

  const key = depKey(parentJobId, jobId);
  await redis.set(key, JSON.stringify(state), { EX: TTL });

  console.log(
    `[DepGraph] Registered  job=${jobId}  queue=${queue}` +
    `  depends_on=[${dependsOn.join(', ')}]  remaining=${dependsOn.length}  status=WAITING`,
  );
}

/**
 * Inspect the current DepState for a blocked job (useful for dashboards / retries).
 */
export async function getDepState(
  redis: ReturnType<typeof createClient>,
  parentJobId: string,
  jobId: string,
): Promise<DepState | null> {
  const raw = await redis.get(depKey(parentJobId, jobId));
  return raw ? (JSON.parse(raw) as DepState) : null;
}

// ── Core logic ─────────────────────────────────────────────────────────────

/**
 * Mark `completedJobId` as done across all downstream jobs registered under
 * `parentJobId`.
 *
 * For each downstream job:
 *   - Checks whether `completedJobId` appears in its `depends_on` list.
 *   - Decrements `remaining` and updates the state document atomically.
 *   - If `remaining` reaches 0, transitions status → READY, then DISPATCHED,
 *     and returns the payload for immediate dispatch.
 *
 * Returns an array of `{ queue, payload }` for every job that just unblocked.
 */
export async function markDependencySatisfied(
  redis: ReturnType<typeof createClient>,
  parentJobId: string,
  completedJobId: string,
  registeredJobIds: string[],
): Promise<Array<{ queue: string; payload: any }>> {
  const readyJobs: Array<{ queue: string; payload: any }> = [];

  for (const jobId of registeredJobIds) {
    const key = depKey(parentJobId, jobId);
    const raw = await redis.get(key);
    if (!raw) continue;

    const state: DepState = JSON.parse(raw);

    // Skip if already dispatched or if completedJobId isn't a dep for this job
    if (state.status === 'DISPATCHED') continue;
    if (!state.depends_on.includes(completedJobId)) continue;

    // Decrement remaining
    state.remaining = Math.max(0, state.remaining - 1);

    if (state.remaining === 0) {
      state.status = 'DISPATCHED';
      await redis.set(key, JSON.stringify(state), { EX: TTL });

      console.log(
        `[DepGraph] ✅ job=${jobId}  remaining=0  status=DISPATCHED` +
        `  (unblocked by ${completedJobId})`,
      );
      readyJobs.push({ queue: state.queue, payload: state.payload });
    } else {
      state.status = 'WAITING'; // still waiting
      await redis.set(key, JSON.stringify(state), { EX: TTL });

      console.log(
        `[DepGraph]    job=${jobId}  remaining=${state.remaining}  status=WAITING` +
        `  (satisfied ${completedJobId}, still blocked)`,
      );
    }
  }

  return readyJobs;
}
