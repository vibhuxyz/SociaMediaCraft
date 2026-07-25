import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import amqp from 'amqplib';
import multer from 'multer';
import multerS3 from 'multer-s3';
import { S3Client } from '@aws-sdk/client-s3';
import { prisma } from '@videocraft/database'; // <--- V2 Import

dotenv.config({ path: '../../.env' });

const app = express();
const port = process.env.PORT || 8080;

app.use(cors());
app.use(express.json());

// 1. MinIO (S3-compatible) setup
const s3Client = new S3Client({
  endpoint: process.env.MINIO_ENDPOINT || 'http://localhost:9000',
  region: 'us-east-1', // Required by AWS SDK but ignored by MinIO
  credentials: {
    accessKeyId: process.env.MINIO_ACCESS_KEY || 'minioadmin',
    secretAccessKey: process.env.MINIO_SECRET_KEY || 'minioadmin',
  },
  forcePathStyle: true, // Crucial for MinIO compatibility
});

const upload = multer({
  storage: multerS3({
    s3: s3Client,
    bucket: process.env.S3_BUCKET || 'uploads',
    acl: 'public-read',
    metadata: function (req, file, cb) {
      cb(null, { fieldName: file.fieldname });
    },
    key: function (req, file, cb) {
      cb(null, Date.now().toString() + '-' + file.originalname);
    }
  })
});

// 2. RabbitMQ setup
const RABBITMQ_URL = process.env.RABBITMQ_URL || 'amqp://user:password@localhost:5672';

app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'api-gateway' });
});

// Endpoint: Upload a file directly to MinIO
app.post('/api/upload', upload.single('file'), (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }
    
    // multer-s3 adds the location/key to req.file
    const fileData = req.file as any;
    res.json({ 
      message: 'File uploaded successfully', 
      url: fileData.location || `http://localhost:9000/${process.env.S3_BUCKET || 'uploads'}/${fileData.key}`,
      key: fileData.key
    });
  } catch (error) {
    console.error('Error uploading file:', error);
    res.status(500).json({ error: 'File upload failed' });
  }
});

// Endpoint: Queue a Job (V0 Legacy)
app.post('/api/jobs', async (req, res) => {
  try {
    const { type, payload } = req.body;
    
    // Connect to RabbitMQ
    const connection = await amqp.connect(RABBITMQ_URL);
    const channel = await connection.createChannel();
    
    const queue = 'ai_jobs';
    await channel.assertQueue(queue, { durable: true });
    
    // Send job to queue
    const jobData = { id: Date.now().toString(), type, payload };
    channel.sendToQueue(queue, Buffer.from(JSON.stringify(jobData)), { persistent: true });
    
    console.log(`[API Gateway] Job sent to queue:`, jobData.id);
    
    setTimeout(() => {
      connection.close();
    }, 500);
    
    res.status(202).json({ message: 'Job accepted', jobId: jobData.id });
  } catch (error) {
    console.error('Error queuing job:', error);
    res.status(500).json({ error: 'Failed to queue job' });
  }
});

// V2 Endpoint: Polling endpoint for the Frontend to check Job status
app.get('/api/jobs/:id', async (req, res) => {
  try {
    const job = await prisma.job.findUnique({
      where: { id: req.params.id }
    });
    
    if (!job) return res.status(404).json({ error: 'Job not found' });
    
    res.json(job);
  } catch (error) {
    console.error('Error fetching job:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// V1/V2 Endpoint: Generate a Video Plan (Producer)
app.post('/api/plan', async (req, res) => {
  try {
    const { prompt } = req.body;
    if (!prompt) return res.status(400).json({ error: 'Prompt is required' });
    
    // 1. V2 DB Integration: Create the Job in Postgres as "PENDING"
    const job = await prisma.job.create({
      data: {
        type: 'VIDEO_PLAN',
        status: 'PENDING',
        payload: { prompt }
      }
    });
    
    // 2. Connect to RabbitMQ
    const connection = await amqp.connect(RABBITMQ_URL);
    const channel = await connection.createChannel();
    
    const queue = 'orchestrator_queue';
    await channel.assertQueue(queue, { durable: true });
    
    // 3. Send the generic job to Orchestrator so it can determine the workflow
    const message = { id: job.id, type: 'youtube_video', prompt };
    channel.sendToQueue(queue, Buffer.from(JSON.stringify(message)), { persistent: true });
    
    console.log(`[API Gateway] Saved to DB & Sent to RabbitMQ:`, job.id);
    
    setTimeout(() => {
      connection.close();
    }, 500);
    
    // 4. Return the Postgres Job ID to the React Frontend so it can start polling!
    res.status(202).json({ message: 'Plan generation started!', planId: job.id });
  } catch (error) {
    console.error('Error queuing plan:', error);
    res.status(500).json({ error: 'Failed to queue plan' });
  }
});

import { initS3Bucket } from './init-s3';

app.listen(port, async () => {
  // Initialize the MinIO bucket before accepting traffic
  await initS3Bucket(s3Client, process.env.S3_BUCKET || 'uploads');
  console.log(`API Gateway running on port ${port}`);
});
