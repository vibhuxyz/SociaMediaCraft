import { useState, useEffect, useRef } from 'react';
import { Loader2, CheckCircle2, Clock, Play, AlertCircle, Sparkles, LayoutTemplate, Activity } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { generatePlan, getPlanStatus, type JobState } from '../../../services/v2';

interface ProgressEvent {
  type: 'progress' | 'completed' | 'failed';
  stage?: string;
  progress?: number;
  message?: string;
  result?: any;
}

export function V2Page() {
  const [prompt, setPrompt] = useState('Create a YouTube Short explaining black holes for 10-year-olds. Make it spooky.');
  const [jobId, setJobId] = useState<string | null>(null);
  const [jobState, setJobState] = useState<JobState | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [liveEvents, setLiveEvents] = useState<ProgressEvent[]>([]);
  const eventSourceRef = useRef<EventSource | null>(null);

  const startGeneration = async () => {
    setIsLoading(true);
    setJobState(null);
    setLiveEvents([]);
    try {
      const newJobId = await generatePlan(prompt);
      setJobId(newJobId);
      
      const initialJob = await getPlanStatus(newJobId);
      setJobState(initialJob);
    } catch (err) {
      console.error(err);
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (!jobId) return;

    const eventSource = new EventSource(`http://localhost:6001/api/events/${jobId}`);
    eventSourceRef.current = eventSource;

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as ProgressEvent;
        setLiveEvents(prev => {
          if (prev.length > 0 && prev[prev.length - 1].message === data.message) {
            return prev;
          }
          return [...prev, data];
        });
        
        if (data.type === 'completed' || data.type === 'failed') {
          setIsLoading(false);
          eventSource.close();
        }
      } catch (err) {
      }
    };

    eventSource.onerror = () => {
      console.error('SSE Error. Connection lost.');
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [jobId]);

  const latestEvent = liveEvents[liveEvents.length - 1];

  return (
    <div className="animate-in fade-in slide-in-from-bottom-4 duration-700 w-full max-w-5xl mx-auto space-y-8">
      {/* Header Section */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-indigo-900 via-purple-900 to-slate-900 p-8 sm:p-10 text-white shadow-2xl shadow-indigo-900/20 border border-white/10">
        <div className="absolute top-0 right-0 p-8 opacity-10 pointer-events-none">
          <Sparkles className="w-64 h-64" />
        </div>
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 backdrop-blur-md border border-white/20 text-xs font-medium text-indigo-200 tracking-wide mb-6 shadow-inner">
            <Activity className="w-4 h-4" /> Phase V2: Frontend & Database
          </div>
          <h2 className="text-4xl sm:text-5xl font-extrabold tracking-tight mb-4 bg-clip-text text-transparent bg-gradient-to-r from-white to-indigo-200">
            AI Video Planner
          </h2>
          <p className="text-indigo-200/80 text-lg leading-relaxed max-w-xl">
            Experience our hybrid event-driven architecture. Enter a prompt below to see real-time updates as the AI agents synthesize your video plan.
          </p>
        </div>
      </div>
      
      {/* Main Interaction Area */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Input Panel */}
        <div className="lg:col-span-5 flex flex-col gap-6">
          <div className="bg-white/70 backdrop-blur-xl p-6 sm:p-8 rounded-3xl border border-slate-200/60 shadow-xl shadow-slate-200/40 relative overflow-hidden group transition-all hover:shadow-indigo-500/10">
            <div className="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-indigo-500 to-purple-500" />
            <div className="mb-6">
              <label className="flex items-center gap-2 text-sm font-bold text-slate-800 mb-3 uppercase tracking-wider">
                <LayoutTemplate className="w-4 h-4 text-indigo-500" />
                Video Concept
              </label>
              <textarea 
                rows={4}
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Describe your video idea here..."
                className="w-full p-5 bg-slate-50/50 border border-slate-200 rounded-2xl shadow-inner focus:ring-4 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all text-slate-700 text-base resize-none"
              />
            </div>
            
            <Button 
              onClick={startGeneration} 
              disabled={isLoading}
              className="w-full py-7 text-lg rounded-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white shadow-xl shadow-indigo-500/30 transition-all hover:-translate-y-1 active:translate-y-0"
            >
              {isLoading ? (
                <Loader2 className="w-6 h-6 mr-3 animate-spin" />
              ) : (
                <Sparkles className="w-6 h-6 mr-3" />
              )}
              {isLoading ? 'Generating Plan...' : 'Generate AI Plan'}
            </Button>
          </div>
        </div>

        {/* Output & Timeline Panel */}
        <div className="lg:col-span-7">
          {jobId ? (
            <div className="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200/80 shadow-xl shadow-slate-200/40 h-full flex flex-col animate-in fade-in zoom-in-95 duration-500">
              
              {/* Status Header */}
              <div className="flex items-center justify-between mb-8 pb-6 border-b border-slate-100">
                <div className="flex items-center gap-3">
                  <div className={`p-2.5 rounded-xl ${latestEvent?.type === 'completed' ? 'bg-emerald-100 text-emerald-600' : latestEvent?.type === 'failed' ? 'bg-red-100 text-red-600' : 'bg-indigo-100 text-indigo-600 animate-pulse'}`}>
                    <Clock className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-slate-900">Execution Stream</h3>
                    <p className="text-xs text-slate-500 font-mono mt-0.5">ID: {jobId.split('-')[0]}...</p>
                  </div>
                </div>
                {/* Progress Mini-Badge */}
                <div className="px-4 py-1.5 bg-slate-50 rounded-full border border-slate-200 text-sm font-semibold text-slate-700 shadow-sm">
                  {latestEvent?.type === 'completed' ? '100%' : `${latestEvent?.progress || 0}%`}
                </div>
              </div>

              {/* Progress Bar Line */}
              <div className="w-full bg-slate-100 rounded-full h-1.5 mb-8 overflow-hidden">
                <div 
                  className={`h-full rounded-full transition-all duration-1000 ease-out ${latestEvent?.type === 'completed' ? 'bg-emerald-500' : latestEvent?.type === 'failed' ? 'bg-red-500' : 'bg-gradient-to-r from-indigo-500 to-purple-500'}`} 
                  style={{ width: `${latestEvent?.progress || (latestEvent?.type === 'completed' ? 100 : 0)}%` }}
                />
              </div>

              {/* Live Events List */}
              <div className="flex-1 overflow-y-auto mb-6 pr-2 custom-scrollbar">
                {liveEvents.length === 0 && isLoading && (
                  <div className="flex flex-col items-center justify-center py-12 text-slate-400">
                    <Loader2 className="w-8 h-8 mb-4 animate-spin text-indigo-300" />
                    <p className="text-sm font-medium">Connecting to RabbitMQ Workers...</p>
                  </div>
                )}

                {liveEvents.length > 0 && (
                  <div className="space-y-6">
                    {liveEvents.map((evt, idx) => {
                      const isLast = idx === liveEvents.length - 1;
                      const isFinished = evt.type === 'completed';
                      const isFailed = evt.type === 'failed';
                      
                      return (
                        <div key={idx} className={`flex items-start gap-4 transition-all duration-500 ${isLast ? 'opacity-100 translate-x-0' : 'opacity-40 translate-x-2'}`}>
                          <div className={`mt-0.5 relative z-10 rounded-full bg-white flex items-center justify-center ${isLast && !isFinished && !isFailed ? 'shadow-[0_0_15px_rgba(99,102,241,0.4)]' : ''}`}>
                            {isFailed ? (
                              <AlertCircle className="w-6 h-6 text-red-500 drop-shadow-sm" />
                            ) : (!isLast || isFinished) ? (
                              <CheckCircle2 className="w-6 h-6 text-emerald-500 drop-shadow-sm" />
                            ) : (
                              <Loader2 className="w-6 h-6 text-indigo-500 animate-spin" />
                            )}
                          </div>
                          <div className="flex-1 pb-2">
                            <p className={`text-base font-semibold ${isLast && !isFinished ? 'text-indigo-700' : 'text-slate-700'}`}>
                              {evt.message || "Processing..."}
                            </p>
                            {evt.progress && (
                              <p className="text-sm text-slate-400 mt-1 font-medium">{evt.progress}% Complete</p>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Final Result Display */}
              {latestEvent?.type === 'completed' && latestEvent.result && (
                <div className="mt-auto animate-in fade-in slide-in-from-bottom-4 duration-700 pt-6 border-t border-slate-100">
                  <div className="flex items-center gap-2 mb-3">
                    <Sparkles className="w-4 h-4 text-emerald-500" />
                    <h4 className="text-sm font-bold text-slate-800 uppercase tracking-wider">Generated Plan Payload</h4>
                  </div>
                  <div className="bg-[#0D1117] rounded-2xl p-5 overflow-x-auto shadow-inner border border-slate-800/50">
                    <pre className="text-[#56d364] text-sm font-mono leading-relaxed">
                      {JSON.stringify(
                        typeof latestEvent.result === 'string' ? JSON.parse(latestEvent.result) : latestEvent.result, 
                        null, 2
                      )}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="h-full bg-slate-50/50 backdrop-blur-sm border-2 border-dashed border-slate-200 rounded-3xl flex flex-col items-center justify-center p-12 text-center text-slate-400">
              <div className="w-20 h-20 bg-slate-100 rounded-full flex items-center justify-center mb-6 shadow-inner">
                <Play className="w-8 h-8 text-slate-300 ml-1" />
              </div>
              <h3 className="text-xl font-bold text-slate-600 mb-2">Ready to Orchestrate</h3>
              <p className="max-w-sm text-slate-500">
                Enter your prompt and hit generate to kick off the multi-agent AI pipeline.
              </p>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
