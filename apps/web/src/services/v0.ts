// Version 0: Infrastructure Foundation
// Handles file uploads, job queues, and storage status

export interface JobStatus {
  id: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  url?: string;
  error?: string;
}

export async function uploadImage(file: File): Promise<{ jobId: string }> {
  try {
    // 1. Upload to MinIO via API Gateway
    const formData = new FormData();
    formData.append('file', file);
    
    const uploadRes = await fetch('http://localhost:3001/api/upload', {
      method: 'POST',
      body: formData,
    });
    if (!uploadRes.ok) throw new Error('Failed to upload file to backend');
    const uploadData = await uploadRes.json();

    // 2. Queue the job in RabbitMQ via API Gateway
    const jobRes = await fetch('http://localhost:3001/api/jobs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        type: 'process_image', 
        payload: { fileUrl: uploadData.url, fileKey: uploadData.key } 
      }),
    });
    if (!jobRes.ok) throw new Error('Failed to queue job');
    const jobData = await jobRes.json();

    return { jobId: jobData.jobId };
  } catch {
    console.warn("Backend not available on port 3001, mocking V0 upload...");
    return new Promise(resolve => setTimeout(() => resolve({ jobId: 'job_' + Date.now() }), 1000));
  }
}

export async function checkJobStatus(jobId: string): Promise<JobStatus> {
  try {
    const res = await fetch(`/api/v0/jobs/${jobId}`);
    if (!res.ok) throw new Error('Failed to fetch status');
    return await res.json();
  } catch {
    // Mocking job progression for UI testing
    const random = Math.random();
    let status: JobStatus['status'] = 'queued';
    if (random > 0.8) status = 'completed';
    else if (random > 0.3) status = 'processing';
    
    return new Promise(resolve => setTimeout(() => resolve({
      id: jobId,
      status,
      url: status === 'completed' ? 'https://example.com/mock-image.png' : undefined
    }), 500));
  }
}
