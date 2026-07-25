import amqp from 'amqplib';
import { prisma } from '@videocraft/database';
import { downloadAssets, uploadResults } from '../lib/s3';
import { callPythonAgent } from '../lib/python';
import { connectRedis, publishEvent } from '../lib/redis';

export async function startPlanningWorker(connection: any) {
  const QUEUE_NAME = 'planning_queue';
  const channel = await connection.createChannel();
  
  await channel.assertQueue(QUEUE_NAME, { durable: true });
  channel.prefetch(1);
  
  console.log(`[Worker: Planning] Listening on ${QUEUE_NAME}`);
  
  channel.consume(QUEUE_NAME, async (msg: any) => {
    if (!msg) return;
    const job = JSON.parse(msg.content.toString());
    console.log(`\n📦 [Worker: Planning] Picked up Job: ${job.id}`);
    
    try {
      await connectRedis();
      await prisma.job.update({ where: { id: job.id }, data: { status: 'PROCESSING' } });
      await publishEvent(job.id, 'worker', 'progress', 'Worker preparing assets...', 5);
      
      // 1. Download Assets
      const localDir = await downloadAssets(job.id);
      
      // 2. Prepare Payload & Call Python
      await publishEvent(job.id, 'worker', 'progress', 'Calling Python AI Engine (V2)...', 15);
      const payload = { jobId: job.id, prompt: job.prompt, assetsDir: localDir };
      
      // Trigger the Python V2 Agentic Workflow
      const aiResponse = await callPythonAgent('/api/v2/generate-plan', payload);
      
      // 3. Upload Results
      await publishEvent(job.id, 'worker', 'progress', 'Uploading results to S3...', 90);
      const s3Url = await uploadResults(job.id, aiResponse.result);
      
      // 4. Update Database
      await prisma.job.update({
        where: { id: job.id },
        data: { status: 'COMPLETED', result: aiResponse.result }
      });
      
      // 5. Publish Final Event
      await publishEvent(job.id, 'worker', 'completed', 'Planning Complete!', 100, aiResponse.result);
      
      console.log(`✅ [Worker: Planning] Successfully finished job: ${job.id}`);
      channel.ack(msg);
      
    } catch (err: any) {
      console.error(`❌ [Worker: Planning] Failed:`, err);
      await prisma.job.update({ where: { id: job.id }, data: { status: 'FAILED' } });
      await publishEvent(job.id, 'worker', 'failed', err.message);
      channel.nack(msg, false, false);
    }
  });
}
