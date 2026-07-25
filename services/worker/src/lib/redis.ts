import { createClient } from 'redis';

const REDIS_URL = process.env.REDIS_URL || 'redis://localhost:6379';

export const redisClient = createClient({ url: REDIS_URL });

redisClient.on('error', (err) => console.error('Redis Error', err));

export async function connectRedis() {
  if (!redisClient.isOpen) {
    await redisClient.connect();
  }
}

export async function publishEvent(jobId: string, stage: string, type: 'progress' | 'completed' | 'failed', message?: string, progress?: number, result?: any) {
  const payload = {
    jobId,
    type,
    stage,
    message,
    progress,
    result
  };
  // Publish to the typed event bus: job.123.progress
  const channel = `job.${jobId}.${type}`;
  await redisClient.publish(channel, JSON.stringify(payload));
}
