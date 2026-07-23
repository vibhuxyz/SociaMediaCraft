import { useState } from 'react';
import { Loader2, Wrench } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { selectTools, type ToolSelection } from '../../../services/v3';

export function V3Page() {
  const [v3Prompt, setV3Prompt] = useState('I need a video ad and a static poster for Instagram.');
  const [v3Tools, setV3Tools] = useState<ToolSelection[]>([]);
  const [v3Loading, setV3Loading] = useState(false);

  const handleV3Submit = async () => {
    setV3Loading(true);
    try {
      const tools = await selectTools(v3Prompt);
      setV3Tools(tools);
    } finally {
      setV3Loading(false);
    }
  };

  return (
    <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-slate-900">Version 3: Tool Calling</h2>
        <p className="text-slate-500 mt-1">Test MCP/Langchain dynamic tool selection based on intent.</p>
      </div>
      
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
        <div className="mb-4">
          <label className="block text-sm font-medium text-slate-700 mb-2">Request (e.g. Video, Poster, Search)</label>
          <input 
            type="text"
            value={v3Prompt}
            onChange={(e) => setV3Prompt(e.target.value)}
            className="w-full p-3 border border-slate-300 rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
          />
        </div>
        <Button onClick={handleV3Submit} disabled={v3Loading}>
          {v3Loading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
          Select Tools
        </Button>

        {v3Tools.length > 0 && (
          <div className="mt-6 grid grid-cols-1 gap-3">
            <h3 className="font-semibold text-slate-800 mb-2">Selected Tools</h3>
            {v3Tools.map((t, i) => (
              <div key={i} className="flex items-center gap-4 p-4 border border-indigo-100 bg-indigo-50/50 rounded-lg">
                <Wrench className="w-5 h-5 text-indigo-600" />
                <div>
                  <p className="text-sm font-bold text-indigo-900">{t.tool}</p>
                  <p className="text-xs text-indigo-700">{t.reason}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
