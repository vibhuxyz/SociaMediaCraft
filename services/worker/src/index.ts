import amqp from 'amqplib';
import dotenv from 'dotenv';

dotenv.config({ path: '../../.env' });

const RABBITMQ_URL = process.env.RABBITMQ_URL || 'amqp://user:password@localhost:5672';
const QUEUE_NAME = 'ai_jobs';

async function startWorker() {
  try {
    const connection = await amqp.connect(RABBITMQ_URL);
    const channel = await connection.createChannel();
    
    await channel.assertQueue(QUEUE_NAME, { durable: true });
    channel.prefetch(1); // Process one message at a time
    
    console.log(`[Worker] Waiting for messages in queue: ${QUEUE_NAME}`);
    
    channel.consume(QUEUE_NAME, async (msg) => {
      if (msg !== null) {
        const job = JSON.parse(msg.content.toString());
        console.log(`[Worker] Processing job:`, job.id);
        
        // Mock processing time
        await new Promise((resolve) => setTimeout(resolve, 2000));
        
        console.log(`[Worker] Completed job:`, job.id);
        channel.ack(msg);
      }
    });
  } catch (error) {
    console.error('Worker failed to connect:', error);
    setTimeout(startWorker, 5000); // Retry after 5 seconds
  }
}

startWorker();
