import amqp from 'amqplib';

// amqplib's shipped types don't line up with the real return shape of
// amqp.connect() (a longstanding @types/amqplib issue) - `any` here matches
// the same workaround already used elsewhere in this codebase for it.
let connection: any = null;
let channel: any = null;

export async function connectRabbitMQ(url: string) {
  if (!connection) {
    connection = await amqp.connect(url);
    channel = await connection.createChannel();
    console.log('[Worker] Connected to RabbitMQ (publisher)');
  }
  return channel;
}

export async function dispatchTask(queueName: string, payload: any) {
  if (!channel) throw new Error('RabbitMQ channel not initialized');

  await channel.assertQueue(queueName, { durable: true });
  channel.sendToQueue(queueName, Buffer.from(JSON.stringify(payload)), { persistent: true });
  console.log(`[Worker] Dispatched task to ${queueName}`);
}
