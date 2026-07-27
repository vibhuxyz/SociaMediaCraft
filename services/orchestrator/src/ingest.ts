import fs from 'fs';
import path from 'path';
import { connectRabbitMQ } from './lib/rabbitmq';
import { buildJobs } from './jobs/builder';

const RABBITMQ_URL = process.env.RABBITMQ_URL || 'amqp://user:password@localhost:5672';
const AI_ENGINE_URL = process.env.AI_ENGINE_URL || 'http://localhost:8000';

/** Fix #2: Push the full ProjectContext to the AI Engine's Redis store (once per job). */
async function storeProjectContext(jobId: string, projectContext: any): Promise<void> {
  const resp = await fetch(`${AI_ENGINE_URL}/api/v1/store-context`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ job_id: jobId, context: projectContext }),
  });
  if (!resp.ok) {
    console.warn(`⚠️ [Orchestrator] Could not store context (AI Engine unreachable): ${resp.statusText}`);
  } else {
    console.log(`✅ [Orchestrator] ProjectContext stored in AI Engine Redis for job ${jobId}`);
  }
}

async function ingestCreativePlan() {
  console.log('🎼 [Orchestrator] Ingesting Creative Plan...');
  
  const rootDir = path.resolve(__dirname, '../../../');
  const planPath = path.join(rootDir, 'final.json');
  
  if (!fs.existsSync(planPath)) {
    console.error(`❌ [Orchestrator] final.json not found at ${planPath}`);
    process.exit(1);
  }
  
  const creativePlan = JSON.parse(fs.readFileSync(planPath, 'utf8'));
  
  // 1. Build Jobs & Context
  const { projectContext, jobs } = buildJobs(creativePlan);
  console.log(`✅ [Orchestrator] Created Project Context: ${projectContext.context_id}`);
  console.log(`✅ [Orchestrator] Generated ${jobs.length} Immutable Jobs.`);
  
  // 2. Fix #2: Store ProjectContext in the AI Engine (real call)
  await storeProjectContext(projectContext.context_id, projectContext);
  console.log(`✅ [Orchestrator] ProjectContext stored for context: ${projectContext.context_id}`);
  
  // 3. Connect to RabbitMQ
  let channel;
  try {
    channel = await connectRabbitMQ(RABBITMQ_URL);
  } catch (e) {
    console.warn('⚠️ [Orchestrator] Could not connect to real RabbitMQ, mocking publish...');
  }
  
  // 4. Publish Jobs to RabbitMQ
  console.log(`\n🚀 [Orchestrator] Publishing ${jobs.length} jobs to respective RabbitMQ queues...`);
  
  const queueStats: Record<string, number> = {};
  
  for (const job of jobs) {
    const queue = job.queue || 'default';
    if (!queueStats[queue]) queueStats[queue] = 0;
    queueStats[queue]++;
    
    // Fix #1: Send thin descriptor — AI Engine resolves context and builds prompt.
    // job.prompt (the full pre-built string from builder.ts) is kept as base_prompt
    // so the AI Engine has the raw scene intent to start from.
    const payload = {
      context_id: projectContext.context_id,
      job: {
        ...job,
        job_id_parent: projectContext.context_id,  // AI Engine needs this to load context
        base_prompt: job.prompt,                   // rename: Worker no longer builds final prompt
      }
    };
    
    if (channel) {
      await channel.assertQueue(queue, { durable: true });
      channel.sendToQueue(queue, Buffer.from(JSON.stringify(payload)), {
        persistent: true,
        priority: job.priority || 0
      });
    }
    
    console.log(`   -> [PUBLISHED] [${queue}] { context_id: '${projectContext.context_id}', job_id: '${job.job_id}' }`);
  }
  
  console.log('\n[Orchestrator] RabbitMQ Dispatch Summary:');
  for (const [q, count] of Object.entries(queueStats)) {
    console.log(`   - ${q}: ${count} jobs`);
  }
  
  console.log('\n✅ [Orchestrator] Ingestion Complete. Workers can now begin processing.');
  process.exit(0);
}

ingestCreativePlan().catch(console.error);
