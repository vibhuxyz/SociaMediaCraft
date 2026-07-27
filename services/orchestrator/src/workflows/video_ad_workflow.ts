/**
 * Video Ad Workflow  (formerly youtube-video.ts)
 * ================================================
 * Orchestrates the full pipeline for a multi-scene video advertisement:
 *
 *   Planning → Context Store → Asset Fan-out → Dep Graph → Event-Driven Dispatch
 *
 * This workflow is format-agnostic (YouTube, TikTok, Reels, CTV, etc.).
 * The `workflow` field on the job record controls branding / output specs;
 * the core asset generation logic here is identical for every format.
 *
 * Implements:
 *   Fix #2 — Project Context Store  (store once, resolve per shot)
 *   Fix #3 — Dependency Graph       (video waits for image)
 *   Fix #5 — Event-Driven Dispatch  (react to asset-completed events)
 */

import { createClient } from 'redis';
import { dispatchTask } from '../lib/rabbitmq';
import { connectRedis, publishEvent, setPendingAssetCount } from '../lib/redis';
import { registerJobDependency, markDependencySatisfied } from '../lib/dep_graph';

const AI_ENGINE_URL = process.env.AI_ENGINE_URL || 'http://localhost:8000';
const REDIS_URL     = process.env.REDIS_URL     || 'redis://localhost:6379';

// ---------------------------------------------------------------------------
// Fix: Build ProjectContext from actual production plan fields
// ---------------------------------------------------------------------------
// The CreativePlan produced by the AI engine has NO "project_context" key.
// It stores characters under `characters.character_sheets`, environments
// under `environment.locations`, brand under `brand_identity`, and so on.
// This function extracts and normalises those into the shape the AI Engine's
// context_store expects.

function buildProjectContextFromPlan(jobId: string, plan: any): any {
  const chars   = plan.characters?.character_sheets || [];
  const locs    = plan.environment?.locations        || [];
  const brand   = plan.brand_identity               || {};
  const art     = plan.art_direction                || {};
  const cinema  = plan.cinematography               || {};

  return {
    context_id: jobId,
    metadata: { project_id: jobId, workflow: 'v4.2' },

    brand: {
      brand_id:    'brand_001',
      colors:      brand.color_palette  || [],
      logo_rules:  brand.logo_rules     || '',
      personality: brand.brand_personality || '',
    },

    art_direction: {
      visual_style:  art.visual_style   || cinema.visual_style  || 'Cinematic',
      camera_type:   art.camera_type    || 'Digital Cinema Camera',
      lens:          art.lens           || '35mm',
      color_grading: art.color_grading  || 'Natural',
      aspect_ratio:  cinema.aspect_ratio || '16:9',
    },

    characters: chars.map((c: any, i: number) => ({
      character_id: `char_${i + 1}`,
      name:         c.name       || '',
      appearance:   c.appearance || {},
      outfits:      c.outfits    || [],
    })),

    environments: locs.map((loc: any, i: number) => {
      const isStr = typeof loc === 'string';
      return {
        environment_id: `env_${i + 1}`,
        name:         isStr ? loc : (loc.name          || ''),
        architecture: isStr ? ''  : (loc.architecture  || ''),
        weather:      isStr ? ''  : (loc.weather       || ''),
        lighting:     isStr ? ''  : (loc.lighting      || ''),
        time_of_day:  isStr ? ''  : (loc.time_of_day   || ''),
        props:        isStr ? []  : (loc.key_props      || []),
      };
    }),
  };
}

// ---------------------------------------------------------------------------
// Store + Verify (the invariant gate)
// ---------------------------------------------------------------------------

/** Push the ProjectContext to the AI Engine once per job. */
async function storeProjectContext(jobId: string, projectContext: any): Promise<void> {
  console.log(`[VideoAdWorkflow] 📤 Storing ProjectContext for job ${jobId}…`);
  console.log(`[VideoAdWorkflow]    Redis key will be: job:${jobId}:project_context`);
  console.log(`[VideoAdWorkflow]    Characters: ${projectContext.characters?.length ?? 0}, Environments: ${projectContext.environments?.length ?? 0}`);

  const resp = await fetch(`${AI_ENGINE_URL}/api/v1/store-context`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ job_id: jobId, context: projectContext }),
  });
  if (!resp.ok) {
    throw new Error(`[VideoAdWorkflow] store-context HTTP ${resp.status}: ${resp.statusText}`);
  }
  console.log(`[VideoAdWorkflow] ✅ ProjectContext stored for job ${jobId}`);
}

/**
 * Verify the context key actually exists in Redis before dispatching any jobs.
 * Calls the AI Engine's /api/v1/context-status endpoint which does a real Redis GET.
 *
 * This is the invariant gate — no job is ever published unless its prerequisite
 * context is confirmed present.
 */
async function verifyContextStored(jobId: string): Promise<void> {
  const resp = await fetch(`${AI_ENGINE_URL}/api/v1/context-status/${jobId}`);
  if (!resp.ok) {
    throw new Error(`[VideoAdWorkflow] context-status HTTP ${resp.status} for job ${jobId}`);
  }
  const body = await resp.json() as { exists: boolean; key: string };
  if (!body.exists) {
    throw new Error(
      `[VideoAdWorkflow] ❌ Context verification FAILED for job ${jobId}. ` +
      `Redis key "${body.key}" not found. ` +
      `No jobs will be dispatched until context storage is confirmed.`
    );
  }
  console.log(`[VideoAdWorkflow] ✅ Context verified in Redis: ${body.key}`);
}

// ---------------------------------------------------------------------------
// Step 1 — Planning dispatch
// ---------------------------------------------------------------------------

export async function executeVideoAdWorkflow(job: any) {
  console.log(`\n🎬 [VideoAdWorkflow] Starting for Job: ${job.id}`);
  console.log(`[VideoAdWorkflow] -> Dispatching to planning_queue`);

  await dispatchTask('planning_queue', {
    id:       job.id,
    prompt:   job.prompt,
    workflow: job.type || 'video_ad',
    step:     'planning',
  });
}

// ---------------------------------------------------------------------------
// Step 2 — Asset dispatch (Fix #2 + Fix #3)
// Called when the planning worker hands off a finished production plan.
// ---------------------------------------------------------------------------

export async function dispatchAssetGeneration(jobId: string, productionPlan: any) {
  console.log(`\n🎬 [VideoAdWorkflow] Plan ready for Job: ${jobId} — dispatching asset generation`);

  await connectRedis();

  // ── Step 1: Build ProjectContext from the actual plan fields ────────────
  // The AI engine's production plan has NO "project_context" key.
  // Characters live at plan.characters.character_sheets, environments at
  // plan.environment.locations, etc. We normalise them here.
  const projectContext = buildProjectContextFromPlan(jobId, productionPlan);

  // ── Step 2: Store context (awaited — this MUST complete first) ──────────
  await storeProjectContext(jobId, projectContext);

  // ── Step 3: Verify the key is actually in Redis ─────────────────────────
  // If the write failed silently or the Redis connection is wrong, this will
  // throw and prevent any job from being dispatched with a missing prereq.
  await verifyContextStored(jobId);

  // ── Step 4: Build the task list ─────────────────────────────────────────
  const scenes = productionPlan?.prompt_pack?.scenes || [];
  type Task = { queue: string; jobId: string; dependsOn: string[]; payload: any };
  const tasks: Task[] = [];

  const firstChar = projectContext.characters?.[0]?.character_id ?? '';
  const firstEnv  = projectContext.environments?.[0]?.environment_id ?? '';

  for (const scene of scenes) {
    for (const shot of scene.shots || []) {
      // ── Images (no upstream deps) ───────────────────────────────────────
      for (const img of shot.images || []) {
        const id = `img_${shot.shot_id}_${tasks.length}`;
        tasks.push({
          queue:     'image-generation',
          jobId:     id,
          dependsOn: [],
          payload: {
            context_id: jobId,
            job: {
              job_id:         id,
              job_id_parent:  jobId,
              parent_job_id:  jobId,
              base_prompt:    img.prompt || '',
              negative_prompt: img.negative_prompt || '',
              strategy:       img.strategy || 'auto',
              preferred_provider: img.provider || undefined,
              references: {
                character_id:   img.character_id   || firstChar,
                environment_id: img.environment_id || firstEnv,
              },
              generation: img,
            },
          },
        });
      }

      // ── Videos (depend on all images for this shot) ────────────────────
      for (const vid of shot.videos || []) {
        const id = `vid_${shot.shot_id}_${tasks.length}`;

        // Fix #3: collect image job IDs for this shot as upstream deps
        const imageDeps = tasks
          .filter(t =>
            t.queue === 'image-generation' &&
            t.payload.job.job_id.includes(`_${shot.shot_id}_`)
          )
          .map(t => t.payload.job.job_id);

        tasks.push({
          queue:     'video-generation',
          jobId:     id,
          dependsOn: imageDeps,
          payload: {
            context_id: jobId,
            job: {
              job_id:         id,
              job_id_parent:  jobId,
              parent_job_id:  jobId,
              base_prompt:    vid.prompt || '',
              strategy:       vid.strategy || 'auto',
              preferred_provider: vid.provider || undefined,
              references: {
                character_id:   vid.character_id   || firstChar,
                environment_id: vid.environment_id || firstEnv,
              },
              generation:       vid,
              input_image_urls: [],
            },
            _queue: 'video-generation',
          },
        });
      }
    }
  }

  if (tasks.length === 0) {
    console.log(`[VideoAdWorkflow] No renderable shots found for Job: ${jobId}`);
    await publishEvent(jobId, 'orchestrator', 'completed', 'Plan generated with no renderable shots.', 100);
    return;
  }

  // Total tracked = all tasks (immediate + dep-blocked)
  await setPendingAssetCount(jobId, tasks.length);

  // ── Separate client for Pub/Sub (can't share with command client) ───────
  const subClient   = createClient({ url: REDIS_URL });
  const writeClient = createClient({ url: REDIS_URL });
  await subClient.connect();
  await writeClient.connect();

  // ── Fix #3: Register deps & dispatch ready jobs ─────────────────────────
  const registeredJobIds: string[] = [];
  let   dispatchedCount            = 0;

  for (const task of tasks) {
    if (task.dependsOn.length === 0) {
      await dispatchTask(task.queue, task.payload);
      dispatchedCount++;
    } else {
      await registerJobDependency(
        writeClient,
        jobId,
        task.jobId,
        task.queue,
        task.dependsOn,
        { ...task.payload, _queue: task.queue },
      );
      registeredJobIds.push(task.jobId);
    }
  }

  console.log(
    `[VideoAdWorkflow] Dispatched ${dispatchedCount} immediate jobs; ` +
    `${registeredJobIds.length} held in dependency graph — Job: ${jobId}`
  );

  if (registeredJobIds.length === 0) {
    await subClient.disconnect();
    await writeClient.disconnect();
    return;
  }

  // ── Fix #5: Subscribe to asset-completed and react ─────────────────────
  const eventChannel = `job.${jobId}.asset-completed`;
  console.log(`[VideoAdWorkflow] 🔔 Subscribed to ${eventChannel}`);

  await subClient.subscribe(eventChannel, async (message: string) => {
    const event           = JSON.parse(message);
    const completedJobId: string = event.jobId;

    console.log(`\n[VideoAdWorkflow] 📡 asset-completed: ${completedJobId}`);

    // Unblock any downstream jobs whose last dep just cleared
    const readyJobs = await markDependencySatisfied(
      writeClient,
      jobId,
      completedJobId,
      registeredJobIds,
    );

    for (const { queue, payload } of readyJobs) {
      console.log(`[VideoAdWorkflow] ⚡ Dispatching unblocked job ${payload.job?.job_id} → ${queue}`);
      await dispatchTask(queue, payload);
    }

    // Clean up once every asset has reported in
    const remaining = await writeClient.get(`job:${jobId}:pending-assets`);
    if (remaining !== null && parseInt(remaining) <= 0) {
      console.log(`[VideoAdWorkflow] 🏁 All assets complete for Job: ${jobId} — unsubscribing`);
      await subClient.unsubscribe(eventChannel);
      await subClient.disconnect();
      await writeClient.disconnect();
    }
  });
}
