// Version 2: Polling & Video Plan Generation

export interface JobState {
  id: string;
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
  result: any;
}

const API_BASE = 'http://localhost:8080/api';

export async function generatePlan(prompt: string): Promise<string> {
  const res = await fetch(`${API_BASE}/plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt }),
  });
  
  if (!res.ok) {
    throw new Error('Failed to start plan generation');
  }
  
  const data = await res.json();
  return data.planId; // Returns the PostgreSQL Job ID
}

export async function getPlanStatus(jobId: string): Promise<JobState> {
  const res = await fetch(`${API_BASE}/jobs/${jobId}`);
  if (!res.ok) {
    throw new Error('Failed to fetch job status');
  }
  return await res.json();
}
