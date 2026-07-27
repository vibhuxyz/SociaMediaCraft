import { createClient } from 'redis';

const REDIS_URL = process.env.REDIS_URL || 'redis://localhost:6379';

export const redisClient = createClient({ url: REDIS_URL });

redisClient.on('error', (err) => console.error('Redis Error', err));

export async function connectRedis() {
  if (!redisClient.isOpen) {
    await redisClient.connect();
  }
}

export async function publishEvent(jobId: string, stage: string, type: 'progress' | 'awaiting-clarification' | 'asset-prompt' | 'asset-generated' | 'completed' | 'failed', message?: string, progress?: number, result?: any, asset?: any) {
  const payload = {
    jobId,
    type,
    stage,
    message,
    progress,
    result,
    asset
  };
  // Publish to the typed event bus: job.123.progress
  const channel = `job.${jobId}.${type}`;
  await redisClient.publish(channel, JSON.stringify(payload));
}

// Pending per-shot asset counter. Orchestrator sets this when it fans out
// image/video generation jobs for a plan; each generic worker decrements it
// as a shot finishes (success or failure) so we know when the whole job is done.
function pendingAssetsKey(jobId: string) {
  return `job:${jobId}:pending-assets`;
}

export async function decrPendingAssetCount(jobId: string): Promise<number> {
  return redisClient.decr(pendingAssetsKey(jobId));
}
