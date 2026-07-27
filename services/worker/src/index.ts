import amqp from 'amqplib';
import dotenv from 'dotenv';
import { startNotificationService } from './notifications/sse';
import { startPlanningWorker } from './workers/planning.worker';
import { startGenericWorker } from './workers/generic.worker';
import { connectRabbitMQ as connectRabbitMQPublisher } from './lib/rabbitmq';

dotenv.config({ path: '../../.env' });

const RABBITMQ_URL = process.env.RABBITMQ_URL || 'amqp://user:password@localhost:5672';
const REDIS_URL = process.env.REDIS_URL || 'redis://localhost:6379';

async function bootstrap() {
  console.log('🚀 Starting Task Workers & Notification Service...');

  // 1. Start Notification Service
  startNotificationService(REDIS_URL, 6001);

  // 2. Connect to RabbitMQ (consumer connection)
  const connection = await amqp.connect(RABBITMQ_URL);
  connection.on('error', (err) => console.error('RabbitMQ Error:', err));

  // 2b. Connect a separate RabbitMQ publisher connection (used to dispatch plan_ready_queue)
  await connectRabbitMQPublisher(RABBITMQ_URL);

  // 3. Mount specific workers
  await startPlanningWorker(connection);
  
  // 4. Mount Generic Media Workers
  const queues = [
    'image-generation',
    'video-generation',
    'voice-generation',
    'music-generation',
    'sfx-generation'
  ];
  
  for (const queue of queues) {
    await startGenericWorker(connection, queue);
  }
}

bootstrap().catch(console.error);
