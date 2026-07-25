import amqp from 'amqplib';
import dotenv from 'dotenv';
import { startNotificationService } from './notifications/sse';
import { startPlanningWorker } from './workers/planning.worker';
// Additional workers (e.g. video.worker.ts, audio.worker.ts) would be imported here

dotenv.config({ path: '../../.env' });

const RABBITMQ_URL = process.env.RABBITMQ_URL || 'amqp://user:password@localhost:5672';
const REDIS_URL = process.env.REDIS_URL || 'redis://localhost:6379';

async function bootstrap() {
  console.log('🚀 Starting Task Workers & Notification Service...');
  
  // 1. Start Notification Service
  startNotificationService(REDIS_URL, 6001);
  
  // 2. Connect to RabbitMQ
  const connection = await amqp.connect(RABBITMQ_URL);
  connection.on('error', (err) => console.error('RabbitMQ Error:', err));
  
  // 3. Mount specific workers
  await startPlanningWorker(connection);
  
  // Later:
  // await startVideoWorker(connection);
  // await startAudioWorker(connection);
}

bootstrap().catch(console.error);
