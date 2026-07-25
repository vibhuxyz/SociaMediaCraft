import { S3Client } from '@aws-sdk/client-s3';

export const s3Client = new S3Client({
  endpoint: process.env.MINIO_ENDPOINT || 'http://localhost:9000',
  region: 'us-east-1', // Required by AWS SDK but ignored by MinIO
  credentials: {
    accessKeyId: process.env.MINIO_ACCESS_KEY || 'minioadmin',
    secretAccessKey: process.env.MINIO_SECRET_KEY || 'minioadmin',
  },
  forcePathStyle: true, // Crucial for MinIO compatibility
});

export async function downloadAssets(jobId: string): Promise<string> {
  console.log(`[S3] Downloading assets for job ${jobId}...`);
  await new Promise(r => setTimeout(r, 500));
  return `/tmp/${jobId}/input`;
}

export async function uploadResults(jobId: string, resultData: any): Promise<string> {
  console.log(`[S3] Uploading results to cloud storage for job ${jobId}...`);
  await new Promise(r => setTimeout(r, 500));
  return `s3://videocraft-results/${jobId}/plan.json`;
}
