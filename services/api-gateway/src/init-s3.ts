import { S3Client, CreateBucketCommand, HeadBucketCommand } from '@aws-sdk/client-s3';

export async function initS3Bucket(s3Client: S3Client, bucketName: string) {
  try {
    // Check if bucket exists
    await s3Client.send(new HeadBucketCommand({ Bucket: bucketName }));
    console.log(`[MinIO] Bucket "${bucketName}" already exists.`);
  } catch (error: any) {
    if (error.name === 'NotFound' || error.$metadata?.httpStatusCode === 404) {
      console.log(`[MinIO] Bucket "${bucketName}" not found. Creating...`);
      try {
        await s3Client.send(new CreateBucketCommand({ Bucket: bucketName }));
        console.log(`[MinIO] Bucket "${bucketName}" created successfully.`);
      } catch (createError) {
        console.error(`[MinIO] Failed to create bucket "${bucketName}":`, createError);
      }
    } else {
      console.error(`[MinIO] Error checking bucket "${bucketName}":`, error);
    }
  }
}
