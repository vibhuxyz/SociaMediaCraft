import dotenv from 'dotenv';
import { connectRabbitMQ } from './lib/rabbitmq';
import { executeYouTubeWorkflow } from './workflows/youtube-video';

dotenv.config({ path: '../../.env' });

const RABBITMQ_URL = process.env.RABBITMQ_URL || 'amqp://user:password@localhost:5672';
const QUEUE_NAME = 'orchestrator_queue';

async function bootstrap() {
  console.log('🎼 Starting Job Orchestrator (The Conductor)...');
  
  const channel = await connectRabbitMQ(RABBITMQ_URL);
  if (!channel) throw new Error('Failed to connect to RabbitMQ');
  
  await channel.assertQueue(QUEUE_NAME, { durable: true });
  channel.prefetch(1);
  
  console.log(`[Orchestrator] Listening for incoming job requests on: ${QUEUE_NAME}`);
  
  channel.consume(QUEUE_NAME, async (msg) => {
    if (!msg) return;
    const job = JSON.parse(msg.content.toString());
    console.log(`\n📦 [Orchestrator] Received Generic Job Request: ${job.id}`);
    
    try {
      // Determine the workflow
      if (job.type === 'youtube_video' || !job.type) {
        await executeYouTubeWorkflow(job);
      } else {
        console.log(`[Orchestrator] Unknown workflow type: ${job.type}`);
      }
      
      channel.ack(msg);
    } catch (err) {
      console.error(`❌ [Orchestrator] Pipeline Dispatch Failed:`, err);
      channel.nack(msg, false, false);
    }
  });
}

bootstrap().catch(console.error);
