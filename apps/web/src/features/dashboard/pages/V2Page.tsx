import { useState } from 'react';
import { Loader2, CheckCircle2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { executeWorkflow, type WorkflowLog } from '../../../services/v2';

export function V2Page() {
  const [v2Prompt, setV2Prompt] = useState('Analyze this script and route to the correct video engine.');
  const [v2Logs, setV2Logs] = useState<WorkflowLog[]>([]);
  const [v2Loading, setV2Loading] = useState(false);

  const handleV2Submit = async () => {
    setV2Loading(true);
    setV2Logs([]);
    try {
      const logs = await executeWorkflow(v2Prompt);
      setV2Logs(logs);
    } finally {
      setV2Loading(false);
    }
  };

  return (
    <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-slate-900">Version 2: Workflow Engine</h2>
        <p className="text-slate-500 mt-1">Test LangGraph DAG execution (Planner -&gt; Storyboard -&gt; Optimizer -&gt; Router).</p>
      </div>
      
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
        <div className="mb-4">
          <label className="block text-sm font-medium text-slate-700 mb-2">Workflow Prompt</label>
          <input 
            type="text"
            value={v2Prompt}
            onChange={(e) => setV2Prompt(e.target.value)}
            className="w-full p-3 border border-slate-300 rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
          />
        </div>
        <Button onClick={handleV2Submit} disabled={v2Loading}>
          {v2Loading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
          Execute Graph
        </Button>

        {v2Logs.length > 0 && (
          <div className="mt-6 space-y-3">
            <h3 className="font-semibold text-slate-800 mb-3">Execution Logs</h3>
            {v2Logs.map((log, i) => (
              <div key={i} className="flex items-start gap-3 p-3 bg-slate-50 border border-slate-100 rounded-lg">
                <div className="mt-0.5">
                  {log.status === 'completed' ? <CheckCircle2 className="w-4 h-4 text-green-500" /> : <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />}
                </div>
                <div>
                  <p className="text-sm font-semibold text-slate-800">{log.node}</p>
                  <p className="text-xs text-slate-500">{log.message}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
