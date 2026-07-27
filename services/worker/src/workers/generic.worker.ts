/**
 * Generic Media Worker  (Fixes #1, #3, #5)
 * ==========================================
 *
 *  Fix #1 — Prompt building moved to AI Engine
 *    The worker no longer constructs or embeds the final Flux/Veo prompt.
 *    It forwards a thin job descriptor (base_prompt + references) directly
 *    to the AI Engine, which resolves context and builds the prompt itself.
 *
 *  Fix #3 + #5 — Dependency Graph + Event-Driven Orchestrator
 *    After every successful asset generation, the worker publishes an
 *    `asset-completed` event on the typed Redis channel:
 *        job.<parentId>.asset-completed
 *    The orchestrator subscribes to this channel and uses it to unblock
 *    any downstream jobs that were waiting for this asset (e.g. video
 *    jobs waiting for an upstream image).
 */

import { prisma } from '@videocraft/database';
import { connectRedis, publishEvent, decrPendingAssetCount, redisClient } from '../lib/redis';

// ---------------------------------------------------------------------------
// Send the thin job descriptor to the AI Engine.
// The AI Engine now owns: context resolution, prompt building, provider call.
// ---------------------------------------------------------------------------

async function sendToAIEngine(queue: string, aiPayload: any): Promise<any> {
  const url = `http://localhost:8000/generate/${queue}`;
  console.log(`     [REST Call] -> ${url}`);

  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(aiPayload),
  });

  if (!response.ok) {
    throw new Error(`AI Engine call failed: ${response.statusText}`);
  }

  return response.json(); // { status, asset_url }
}

// ---------------------------------------------------------------------------
// Worker entry point
// ---------------------------------------------------------------------------

export async function startGenericWorker(connection: any, queueName: string) {
  const channel = await connection.createChannel();
  await channel.assertQueue(queueName, { durable: true });
  channel.prefetch(1); // one job at a time per worker instance

  console.log(`[Worker] Started listening on queue: ${queueName}`);

  channel.consume(queueName, async (msg: any) => {
    if (!msg) return;

    let payload: any;
    try {
      payload = JSON.parse(msg.content.toString());
    } catch {
      console.error(`[Worker] Invalid JSON on ${queueName}`);
      channel.nack(msg, false, false);
      return;
    }

    const { job } = payload;
    const parentJobId = job.parent_job_id || job.job_id_parent;
    const assetType   = queueName === 'video-generation' ? 'video' : 'image';

    console.log(`\n======================================================`);
    console.log(`📥 [Worker][${queueName}] Picked up job: ${job.job_id}`);

    try {
      await connectRedis();

      // ── Notify: prompt about to be generated ────────────────────────────
      // Note: `job.base_prompt` is all we store in the queue now.
      // The AI Engine will assemble the real final prompt from ProjectContext.
      await publishEvent(parentJobId, queueName, 'asset-prompt', 'Generating asset...', undefined, undefined, {
        id: job.job_id,
        type: assetType,
        prompt: job.base_prompt,  // raw intent — the full prompt lives in the AI Engine
      });

      // ── Fix #1: Forward thin descriptor → AI Engine builds the prompt ──
      // The job descriptor already carries job_id_parent so the AI Engine can
      // load the ProjectContext from Redis (Fix #2).
      const result = await sendToAIEngine(queueName, job);

      // ── Notify: asset ready ──────────────────────────────────────────────
      await publishEvent(parentJobId, queueName, 'asset-generated', 'Asset created', undefined, undefined, {
        id: job.job_id,
        type: assetType,
        name: job.job_id,
        url: result.asset_url,
        prompt: job.base_prompt,
      });

      channel.ack(msg);
      console.log(`✅ [Worker][${queueName}] Successfully processed job: ${job.job_id}`);

      // ── Fix #3 + #5: Publish asset-completed so the orchestrator can ────
      // unblock any downstream jobs that depend on this asset (e.g. a
      // video-generation job waiting for this image).
      const completionEvent = JSON.stringify({
        jobId: job.job_id,
        parentJobId,
        assetType,
        assetUrl: result.asset_url,
        queue: queueName,
      });
      await redisClient.publish(`job.${parentJobId}.asset-completed`, completionEvent);
      console.log(`📡 [Worker][${queueName}] Published asset-completed for ${job.job_id}`);

    } catch (err: any) {
      console.error(`❌ [Worker][${queueName}] Job ${job.job_id} failed: ${err.message}`);
      await connectRedis();
      await publishEvent(parentJobId, queueName, 'failed', err.message);
      channel.nack(msg, false, false);
    } finally {
      // Decrement the shared pending-asset counter.
      // When it hits 0 every shot (including dep-blocked ones) has reported in.
      const remaining = await decrPendingAssetCount(parentJobId);
      if (remaining <= 0) {
        await publishEvent(parentJobId, queueName, 'completed', 'Pipeline complete!', 100);
        await prisma.job.update({ where: { id: parentJobId }, data: { status: 'COMPLETED' } });
        console.log(`🏁 [Worker][${queueName}] All assets finished for job: ${parentJobId}`);
      }
    }
  });
}
