import express from 'express';
import cors from 'cors';
import { createClient } from 'redis';

export function startNotificationService(redisUrl: string, port = 3002) {
  const app = express();
  app.use(cors());

  app.get('/api/events/:jobId', async (req, res) => {
    const { jobId } = req.params;
    
    res.writeHead(200, {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive'
    });

    const redisSub = createClient({ url: redisUrl });
    await redisSub.connect();
    // Use the typed event bus pattern from the architecture (job.123.*)
    const pattern = `job.${jobId}.*`;

    // pSubscribe listens to all events for this job (progress, completed, warning, etc.)
    await redisSub.pSubscribe(pattern, (message) => {
      res.write(`data: ${message}\n\n`);
    });

    const keepAlive = setInterval(() => res.write(`:\n\n`), 15000);

    req.on('close', () => {
      clearInterval(keepAlive);
      redisSub.pUnsubscribe(pattern);
      redisSub.quit();
    });
  });

  app.listen(port, () => {
    console.log(`[Notification Service] SSE streaming on port ${port}`);
  });
}
