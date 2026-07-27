import dotenv from 'dotenv';
import { connectRabbitMQ } from './lib/rabbitmq';
import { executeVideoAdWorkflow, dispatchAssetGeneration } from './workflows/video_ad_workflow';

dotenv.config({ path: '../../.env' });

const RABBITMQ_URL = process.env.RABBITMQ_URL || 'amqp://user:password@localhost:5672';
const QUEUE_NAME = 'orchestrator_queue';
const PLAN_READY_QUEUE = 'plan_ready_queue';

async function bootstrap() {
  console.log('🎼 Starting Job Orchestrator (The Conductor)...');

  const channel = await connectRabbitMQ(RABBITMQ_URL);
  if (!channel) throw new Error('Failed to connect to RabbitMQ');

  await channel.assertQueue(QUEUE_NAME, { durable: true });
  await channel.assertQueue(PLAN_READY_QUEUE, { durable: true });
  channel.prefetch(1);

  console.log(`[Orchestrator] Listening for incoming job requests on: ${QUEUE_NAME}`);

  channel.consume(QUEUE_NAME, async (msg) => {
    if (!msg) return;
    const job = JSON.parse(msg.content.toString());
    console.log(`\n📦 [Orchestrator] Received Generic Job Request: ${job.id}`);

    try {
      // Determine the workflow — video_ad covers all video formats
      if (job.type === 'youtube_video' || job.type === 'video_ad' || !job.type) {
        await executeVideoAdWorkflow(job);
      } else {
        console.log(`[Orchestrator] Unknown workflow type: ${job.type}`);
      }

      channel.ack(msg);
    } catch (err) {
      console.error(`❌ [Orchestrator] Pipeline Dispatch Failed:`, err);
      channel.nack(msg, false, false);
    }
  });

  console.log(`[Orchestrator] Listening for finished plans on: ${PLAN_READY_QUEUE}`);

  channel.consume(PLAN_READY_QUEUE, async (msg) => {
    if (!msg) return;
    const { jobId, productionPlan } = JSON.parse(msg.content.toString());

    try {
      await dispatchAssetGeneration(jobId, productionPlan);
      channel.ack(msg);
    } catch (err) {
      console.error(`❌ [Orchestrator] Asset dispatch failed:`, err);
      channel.nack(msg, false, false);
    }
  });
}

bootstrap().catch(console.error);
