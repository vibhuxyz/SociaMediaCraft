// Version 3: Tool Calling
// Tool Registry, LangChain, MCP

export interface ToolSelection {
  tool: string;
  reason: string;
}

export async function selectTools(prompt: string): Promise<ToolSelection[]> {
  try {
    const res = await fetch('/api/v3/tools', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt }),
    });
    if (!res.ok) throw new Error('Failed to select tools');
    return await res.json();
  } catch {
    console.warn("Backend not available, mocking V3 tool selection...");
    const p = prompt.toLowerCase();
    const tools: ToolSelection[] = [];
    
    if (p.includes('video') || p.includes('ad')) {
      tools.push({ tool: 'VideoGenTool', reason: 'User requested video generation' });
    }
    if (p.includes('poster') || p.includes('image')) {
      tools.push({ tool: 'PosterTool', reason: 'User requested static image/poster' });
    }
    if (p.includes('search')) {
      tools.push({ tool: 'SearchTool', reason: 'Requires real-time external data' });
    }
    
    // Default fallback
    if (tools.length === 0) {
      tools.push({ tool: 'TextAnalyzerTool', reason: 'Default fallback for text analysis' });
    }
    
    return new Promise(resolve => setTimeout(() => resolve(tools), 1000));
  }
}
