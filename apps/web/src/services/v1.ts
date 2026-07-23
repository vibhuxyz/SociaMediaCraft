// Version 1: AI Planning Engine
// Structured JSON Output from Planner Agent

export interface PlanOutput {
  intent: string;
  steps: string[];
  estimatedTime: string;
}

export async function generatePlan(prompt: string): Promise<PlanOutput> {
  try {
    const res = await fetch('/api/v1/plan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt }),
    });
    if (!res.ok) throw new Error('Failed to generate plan');
    return await res.json();
  } catch {
    console.warn("Backend not available, mocking V1 plan...");
    return new Promise(resolve => setTimeout(() => resolve({
      intent: `Extracted intent from: "${prompt}"`,
      steps: [
        "1. Analyze context",
        "2. Retrieve relevant data",
        "3. Synthesize response",
        "4. Validate JSON output"
      ],
      estimatedTime: "5s"
    }), 1500));
  }
}
