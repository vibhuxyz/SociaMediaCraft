export async function callPythonAgent(endpoint: string, payload: any) {
  const url = `http://localhost:8000${endpoint}`;
  console.log(`🤖 [Python API] POST ${url}`);
  
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  
  if (!response.ok) {
    throw new Error(`Python Agent failed: ${response.statusText}`);
  }
  
  return response.json();
}
