import amqp from 'amqplib';
import { prisma } from '@videocraft/database';
import { downloadAssets } from '../lib/s3';
import { callPythonAgent } from '../lib/python';
import { connectRedis, publishEvent } from '../lib/redis';
import { dispatchTask } from '../lib/rabbitmq';

export async function startPlanningWorker(connection: any) {
  const QUEUE_NAME = 'planning_queue';
  const channel = await connection.createChannel();

  await channel.assertQueue(QUEUE_NAME, { durable: true });
  channel.prefetch(1);

  console.log(`[Worker: Planning] Listening on ${QUEUE_NAME}`);

  channel.consume(QUEUE_NAME, async (msg: any) => {
    if (!msg) return;
    const job = JSON.parse(msg.content.toString());
    const isResume = !!job.resume;
    console.log(`\n📦 [Worker: Planning] Picked up Job: ${job.id} (${isResume ? 'RESUME' : 'FRESH'})`);

    try {
      await connectRedis();
      await prisma.job.update({ where: { id: job.id }, data: { status: 'PROCESSING' } });
      await publishEvent(
        job.id,
        'worker',
        'progress',
        isResume ? 'Resuming with your answers...' : 'Worker preparing assets...',
        5
      );

      if (!isResume) {
        // 1. Download Assets (mocked)
        await downloadAssets(job.id);
      }

      // 2. Prepare Payload & Call Python
      await publishEvent(job.id, 'worker', 'progress', 'Calling Python AI Engine...', 20);

      const payload: any = { prompt: job.prompt, thread_id: job.id };
      if (isResume) payload.clarification_answers = job.answers;

      // The Python server's real route is /api/v1/generate-plan
      const result = await callPythonAgent('/api/v1/generate-plan', payload);

      // If clarification questions came back, pause here and ask the user
      if (result && result.clarification_questions && result.clarification_questions.length > 0) {
        await prisma.job.update({
          where: { id: job.id },
          data: { status: 'AWAITING_CLARIFICATION', result }
        });
        await publishEvent(job.id, 'worker', 'awaiting-clarification', 'Clarification needed', 50, result);
        console.log(`⏸️  [Worker: Planning] Job awaiting clarification: ${job.id}`);
        channel.ack(msg);
        return;
      }

      // Real production plan is ready — persist it and hand off to the Orchestrator
      // to fan out image/video generation. Status stays PROCESSING until all
      // per-shot generation jobs finish (see generic.worker.ts).
      await prisma.job.update({ where: { id: job.id }, data: { result } });
      await publishEvent(job.id, 'worker', 'progress', 'Plan ready — dispatching asset generation...', 60);

      await dispatchTask('plan_ready_queue', { jobId: job.id, productionPlan: result });

      console.log(`✅ [Worker: Planning] Plan complete, handed off to Orchestrator: ${job.id}`);
      channel.ack(msg);
    } catch (err: any) {
      console.error(`❌ [Worker: Planning] Failed:`, err);
      await prisma.job.update({ where: { id: job.id }, data: { status: 'FAILED' } });
      await publishEvent(job.id, 'worker', 'failed', err.message);
      channel.nack(msg, false, false);
    }
  });
}
