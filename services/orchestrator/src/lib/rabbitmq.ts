import amqp from 'amqplib';

let connection: amqp.Connection | null = null;
let channel: amqp.Channel | null = null;

export async function connectRabbitMQ(url: string) {
  if (!connection) {
    connection = await amqp.connect(url);
    channel = await connection.createChannel();
    console.log('[Orchestrator] Connected to RabbitMQ');
  }
  return channel;
}

export async function dispatchTask(queueName: string, payload: any) {
  if (!channel) throw new Error('RabbitMQ channel not initialized');
  
  await channel.assertQueue(queueName, { durable: true });
  channel.sendToQueue(queueName, Buffer.from(JSON.stringify(payload)), { persistent: true });
  console.log(`[Orchestrator] Dispatched task to ${queueName}`);
}
