import { createClient } from 'redis';

const REDIS_URL = process.env.REDIS_URL || 'redis://localhost:6379';

export const redisClient = createClient({ url: REDIS_URL });

redisClient.on('error', (err) => console.error('Redis Error', err));

export async function connectRedis() {
  if (!redisClient.isOpen) {
    await redisClient.connect();
  }
}

export async function publishEvent(
  jobId: string,
  stage: string,
  type: 'progress' | 'awaiting-clarification' | 'asset-prompt' | 'asset-generated' | 'completed' | 'failed',
  message?: string,
  progress?: number,
  result?: any,
  asset?: any
) {
  const payload = { jobId, type, stage, message, progress, result, asset };
  // Same typed event bus convention as services/worker/src/lib/redis.ts: job.123.progress
  const channel = `job.${jobId}.${type}`;
  await redisClient.publish(channel, JSON.stringify(payload));
}

// Same key convention as services/worker/src/lib/redis.ts's decrPendingAssetCount —
// orchestrator sets the initial count when it fans out shot jobs, workers decrement it.
function pendingAssetsKey(jobId: string) {
  return `job:${jobId}:pending-assets`;
}

export async function setPendingAssetCount(jobId: string, count: number): Promise<void> {
  await redisClient.set(pendingAssetsKey(jobId), count);
}
