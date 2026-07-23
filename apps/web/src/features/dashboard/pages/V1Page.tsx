import { useState } from 'react';
import { Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { generatePlan, type PlanOutput } from '../../../services/v1';
import { usePrevious } from '../../../hooks/usePrevious';

export function V1Page() {
  const [v1Prompt, setV1Prompt] = useState('Create a promotional video for my new coffee brand.');
  const prevV1Prompt = usePrevious(v1Prompt);
  const [v1Plan, setV1Plan] = useState<PlanOutput | null>(null);
  const [v1Loading, setV1Loading] = useState(false);

  const handleV1Submit = async () => {
    setV1Loading(true);
    try {
      const plan = await generatePlan(v1Prompt);
      setV1Plan(plan);
    } finally {
      setV1Loading(false);
    }
  };

  return (
    <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-slate-900">Version 1: AI Planning Engine</h2>
        <p className="text-slate-500 mt-1">Test the Planner Agent's structured JSON output and intent recognition.</p>
      </div>
      
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
        <div className="mb-4">
          <label className="block text-sm font-medium text-slate-700 mb-2">User Prompt</label>
          <textarea 
            rows={3}
            value={v1Prompt}
            onChange={(e) => setV1Prompt(e.target.value)}
            className="w-full p-3 border border-slate-300 rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none resize-none"
          />
          {prevV1Prompt && prevV1Prompt !== v1Prompt && (
            <p className="text-xs text-slate-400 mt-2 flex justify-between">
              <span>Previous: {prevV1Prompt}</span>
              <button onClick={() => setV1Prompt(prevV1Prompt)} className="text-indigo-500 hover:underline">Undo</button>
            </p>
          )}
        </div>
        <Button onClick={handleV1Submit} disabled={v1Loading}>
          {v1Loading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
          Run Planner Agent
        </Button>

        {v1Plan && (
          <div className="mt-6">
            <h3 className="font-semibold text-slate-800 mb-2">Structured JSON Output</h3>
            <pre className="bg-slate-900 text-green-400 p-4 rounded-lg text-sm overflow-x-auto">
              {JSON.stringify(v1Plan, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
