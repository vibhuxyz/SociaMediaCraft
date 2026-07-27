import React, { useState, useEffect } from 'react';
import { Play, Activity, CheckCircle2, CircleDashed, Camera, Film, Music, Mic, Layers, Settings2, Download, Terminal, UploadCloud, MessageSquare, Image as ImageIcon, Send } from 'lucide-react';
import { DirectorPrompt } from '../components/DirectorPrompt';

export function DashboardPage() {
  const [prompt, setPrompt] = useState('Create a 30-second cinematic ad for KRC Coffee Shop emphasizing the cozy morning experience.');
  const [isGenerating, setIsGenerating] = useState(false);
  const [activeStage, setActiveStage] = useState(0);

  // Tracks the current job so we can POST clarification answers against it
  const [jobId, setJobId] = useState<string | null>(null);

  // Interactive AI mode states
  const [aiQuestion, setAiQuestion] = useState<{question: string, options?: string[]} | null>(null);
  const [aiAnswer, setAiAnswer] = useState('');

  // Shows the raw prompt currently being worked on by an image/video generation job,
  // before the mocked asset lands (fed by the 'asset-prompt' SSE event).
  const [currentPrompt, setCurrentPrompt] = useState<string | null>(null);

  // Asset feed state
  const [generatedAssets, setGeneratedAssets] = useState<{id: string, type: 'image' | 'video' | 'audio', url: string, name: string, prompt?: string}[]>([]);

  // Mock stages of generation
  const stages = [
    { id: 'planning', name: 'AI Planning & Direction', icon: <Terminal size={18} /> },
    { id: 'prompting', name: 'Prompt Engineering', icon: <Settings2 size={18} /> },
    { id: 'image', name: 'Image Generation', icon: <Camera size={18} /> },
    { id: 'video', name: 'Video Animation', icon: <Film size={18} /> },
    { id: 'audio', name: 'Voice & Music', icon: <Music size={18} /> },
    { id: 'composition', name: 'Master Composition', icon: <Layers size={18} /> },
  ];

  const [backendEvents, setBackendEvents] = useState<any[]>([]);

  const startPipeline = async (promptSuffix: string = '') => {
    // Clear previous pipeline state
    setGeneratedAssets([]);
    setBackendEvents([]);
    setCurrentPrompt(null);
    setJobId(null);
    setIsGenerating(true);
    setActiveStage(1);

    try {
      // 1. Call real API
      const response = await fetch('http://localhost:8080/api/plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: prompt + promptSuffix })
      });

      const data = await response.json();
      if (!data.planId) {
        console.error("No planId returned from API");
        setIsGenerating(false);
        setActiveStage(0);
        return;
      }

      console.log("Connected to Real API. Job ID:", data.planId);
      setJobId(data.planId);

      // 2. Connect to real SSE Notification Service. This connection stays open
      // across a clarification round-trip (see handleAnswerSubmit) and is only
      // closed on final 'completed'/'failed'.
      const eventSource = new EventSource(`http://localhost:6001/api/events/${data.planId}`);

      eventSource.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          console.log("SSE Event:", payload);
          setBackendEvents(prev => [...prev, payload]);

          if (payload.type === 'progress') {
            // Map real progress (0-100) to stages (1-6)
            if (payload.progress < 25) setActiveStage(1); // Planning
            else if (payload.progress < 50) setActiveStage(2); // Prompting
            else if (payload.progress < 75) setActiveStage(3); // Image
            else if (payload.progress <= 100) setActiveStage(4); // Video
          }

          if (payload.type === 'awaiting-clarification') {
            // The AI paused for real clarification questions - keep the SSE connection open,
            // the user's answer is submitted via handleAnswerSubmit against the same job.
            const questions = payload.result?.clarification_questions || [];
            if (questions.length > 0) {
              // Try to detect if the question provides options (e.g. A), B), C))
              const qText = questions[0];
              const optionsMatch = qText.match(/([A-D]\).*?)(?=[A-D]\)|$)/g);

              if (optionsMatch) {
                 const cleanQuestion = qText.split('A)')[0].trim();
                 setAiQuestion({
                   question: cleanQuestion,
                   options: optionsMatch.map((opt: string) => opt.trim())
                 });
              } else {
                 setAiQuestion({
                   question: qText,
                   options: undefined // Free-text input
                 });
              }
            }
            setIsGenerating(false);
          }

          if (payload.type === 'asset-prompt') {
            // Show what the AI is currently rendering, before the mock asset arrives
            setCurrentPrompt(payload.asset?.prompt || null);
          }

          if (payload.type === 'asset-generated') {
             setCurrentPrompt(null);
             // Append to our assets grid natively!
             setGeneratedAssets(prev => [...prev, {
                id: payload.asset.id || `asset-${Date.now()}`,
                type: payload.asset.type || 'video',
                name: payload.asset.name || 'Motion Render',
                url: payload.asset.url,
                prompt: payload.asset.prompt
             }]);
          }

          if (payload.type === 'completed') {
            eventSource.close();
            // Generation completely finished (plan + all image/video assets)
            setActiveStage(7); // Show final master composition state
            setCurrentPrompt(null);
            setIsGenerating(false);
          }

          if (payload.type === 'failed') {
            eventSource.close();
            console.error("Backend Job Failed:", payload.message);
            setIsGenerating(false);
            setActiveStage(0);
            alert("AI Pipeline Failed: " + payload.message);
          }
        } catch (e) {
          // ignore parsing errors from keep-alives
        }
      };

      eventSource.onerror = () => {
        console.log("SSE Connection closed or errored");
        eventSource.close();
      };

    } catch (error) {
      console.error("API Error...", error);
      setIsGenerating(false);
      setActiveStage(0);
    }
  };

  const handleGenerate = (promptText: string, files: File[]) => {
    // Optionally handle files upload here, then start the pipeline
    startPipeline('');
  };

  const handleAnswerSubmit = async (answerText?: string) => {
    if (!jobId) return;
    const question = aiQuestion?.question ?? '';
    const finalAnswer = answerText || aiAnswer;
    setAiQuestion(null);
    setIsGenerating(true);

    try {
      await fetch(`http://localhost:8080/api/jobs/${jobId}/answer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answers: { [question]: finalAnswer } })
      });
      // No new EventSource needed - the one opened in startPipeline is still alive
      // and will keep receiving 'progress' / 'asset-prompt' / 'asset-generated' / 'completed'.
    } catch (error) {
      console.error("Failed to submit answer", error);
      setIsGenerating(false);
    } finally {
      setAiAnswer('');
    }
  };

  return (
    <div className="min-h-screen bg-[#050505] text-slate-200 font-sans selection:bg-indigo-500/30">
      
      {/* Background ambient glow */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-indigo-600/20 rounded-full blur-[120px]"></div>
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-violet-600/10 rounded-full blur-[120px]"></div>
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-6 py-12">
        
        {/* Header */}
        <header className="flex items-center justify-between mb-12 animate-in fade-in slide-in-from-top-8 duration-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <Film className="text-white w-5 h-5" />
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400 tracking-tight">Omni AI</h1>
              <p className="text-xs text-indigo-400 font-medium tracking-wider uppercase">Production Studio</p>
            </div>
          </div>
          <div className="flex gap-4">
            <a href="/admin/v0" className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 backdrop-blur-md text-sm text-slate-300 hover:bg-white/10 transition-colors">
              <Settings2 className="w-4 h-4 text-slate-400" />
              Dev Console
            </a>
            <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 backdrop-blur-md text-sm text-slate-300">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              Fleet Online
            </div>
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Left Column - Input & Status */}
          <div className="lg:col-span-4 flex flex-col gap-6 animate-in fade-in slide-in-from-bottom-8 duration-700 delay-100">
            
            {/* Prompt Input Component */}
            <DirectorPrompt
              initialPrompt={prompt}
              isGenerating={isGenerating}
              onGenerate={handleGenerate}
              aiQuestion={aiQuestion}
              onAnswerSubmit={(answer) => {
                setAiAnswer('');
                handleAnswerSubmit(answer);
              }}
            />

            {/* Pipeline Status */}
            <div className="p-6 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-xl shadow-2xl">
              <h2 className="text-sm font-semibold text-slate-400 mb-6 uppercase tracking-wider">Pipeline Status</h2>
              <div className="space-y-6">
                {stages.map((stage, index) => {
                  const isActive = activeStage === index + 1;
                  const isPast = activeStage > index + 1;
                  const isFuture = activeStage === 0 || activeStage < index + 1;

                  return (
                    <div key={stage.id} className={`flex items-center gap-4 transition-all duration-500 ${isActive ? 'opacity-100 scale-105' : isPast ? 'opacity-50' : 'opacity-30'}`}>
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center border ${
                        isActive ? 'bg-indigo-500/20 border-indigo-500/50 text-indigo-400' : 
                        isPast ? 'bg-emerald-500/20 border-emerald-500/50 text-emerald-400' : 
                        'bg-white/5 border-white/10 text-slate-500'
                      }`}>
                        {isPast ? <CheckCircle2 size={16} /> : isActive ? <Activity size={16} className="animate-spin" /> : <CircleDashed size={16} />}
                      </div>
                      <div className="flex-1">
                        <p className={`text-sm font-medium ${isActive ? 'text-white' : 'text-slate-300'}`}>{stage.name}</p>
                        {isActive && (
                          <div className="h-1 w-full bg-white/10 rounded-full mt-2 overflow-hidden">
                            <div className="h-full bg-indigo-500 w-1/2 rounded-full animate-[progress_2s_ease-in-out_infinite]"></div>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
            
          </div>

          {/* Right Column - Timeline & Viewer */}
          <div className="lg:col-span-8 flex flex-col gap-6 animate-in fade-in slide-in-from-bottom-8 duration-700 delay-200">
            
            {/* Main Viewer */}
            <div className="aspect-video rounded-2xl bg-black/60 border border-white/10 backdrop-blur-xl shadow-2xl overflow-hidden relative group flex items-center justify-center">
              {activeStage === 0 ? (
                <div className="text-center text-slate-500">
                  <Film size={48} className="mx-auto mb-4 opacity-20" />
                  <p className="text-sm">Awaiting prompt to begin production</p>
                </div>
              ) : activeStage > stages.length ? (
                <div className="absolute inset-0 animate-in fade-in duration-1000 flex bg-black">
                  {/* Left: Video */}
                  <div className="w-2/3 h-full relative border-r border-white/10">
                    <video 
                      autoPlay 
                      loop 
                      muted 
                      playsInline 
                      className="absolute inset-0 w-full h-full object-cover opacity-80 mix-blend-luminosity"
                      src={generatedAssets.length > 0 ? generatedAssets[generatedAssets.length - 1].url : ""}
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent"></div>
                    <div className="absolute bottom-6 left-6 right-6 flex items-end justify-between">
                      <div>
                        <h3 className="text-xl font-bold text-white mb-1">final_master_ad.mp4</h3>
                        <p className="text-xs text-slate-300 flex items-center gap-2">
                          <CheckCircle2 size={14} className="text-emerald-400" />
                          Rendering Complete • Master
                        </p>
                      </div>
                      <button className="px-4 py-2 rounded-xl bg-white/10 hover:bg-white/20 border border-white/20 backdrop-blur-md text-white transition-all flex items-center gap-2 text-sm">
                        <Download size={16} />
                        Download
                      </button>
                    </div>
                  </div>
                  
                  {/* Right: Master Script & Iterate */}
                  <div className="w-1/3 h-full flex flex-col bg-[#0a0a0a] relative z-10 overflow-hidden">
                    <div className="p-4 border-b border-white/10 flex items-center gap-2 bg-white/5">
                      <Settings2 size={16} className="text-indigo-400" />
                      <h3 className="text-sm font-bold text-white uppercase tracking-wider">Final Master Script</h3>
                    </div>
                    
                    <div className="flex-1 overflow-y-auto p-4 space-y-4">
                      {generatedAssets.map((asset, i) => (
                        <div key={asset.id} className="bg-white/5 border border-white/10 p-3 rounded-xl">
                          <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider block mb-1">Scene {i + 1}</span>
                          <p className="text-xs text-slate-300 font-mono leading-relaxed">{asset.prompt}</p>
                        </div>
                      ))}
                    </div>

                    <div className="p-4 border-t border-white/10 bg-black/40">
                      <div className="flex gap-2">
                        <input 
                          type="text"
                          value={aiAnswer}
                          onChange={(e) => setAiAnswer(e.target.value)}
                          placeholder="Command LLM to refine..."
                          className="flex-1 bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-xs text-white focus:ring-1 focus:ring-indigo-500 outline-none"
                        />
                        <button 
                          onClick={() => {
                            setGeneratedAssets([]);
                            setActiveStage(1);
                            startPipeline(`[Refinement Command: ${aiAnswer}]`);
                            setAiAnswer('');
                          }}
                          className="px-3 py-2 rounded-lg bg-indigo-500 text-white font-medium hover:bg-indigo-600 transition-colors flex items-center justify-center"
                        >
                          <Send size={14} />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="absolute inset-0 flex flex-col items-center justify-center animate-in fade-in duration-500 overflow-hidden bg-black">
                  {generatedAssets.length > 0 ? (
                    <>
                      {/* Dynamic Stitching Grid */}
                      <div className={`absolute inset-0 grid gap-1 ${
                        generatedAssets.length === 1 ? 'grid-cols-1' : 
                        generatedAssets.length === 2 ? 'grid-cols-2' : 
                        'grid-cols-2 grid-rows-2'
                      }`}>
                        {generatedAssets.map((asset, i) => (
                          <div key={asset.id} className="relative w-full h-full overflow-hidden animate-in zoom-in duration-700 group">
                            <video 
                              autoPlay 
                              loop 
                              muted 
                              playsInline 
                              className="absolute inset-0 w-full h-full object-cover opacity-60 mix-blend-luminosity group-hover:opacity-40 transition-opacity"
                              src={asset.url}
                            />
                            <div className="absolute inset-0 bg-gradient-to-t from-black via-black/50 to-transparent opacity-80"></div>
                            
                            <div className="absolute bottom-4 left-4 right-4 flex flex-col gap-2">
                              <div className="flex items-center justify-between">
                                <span className="text-xs font-bold text-indigo-400 bg-black/80 px-2 py-1 rounded backdrop-blur-md uppercase tracking-wider">
                                  Scene {i + 1}
                                </span>
                              </div>
                              <div className="text-[10px] sm:text-xs text-slate-300 leading-relaxed font-mono bg-black/60 p-3 rounded-lg border border-white/10 backdrop-blur-md max-h-24 overflow-y-auto">
                                <span className="text-emerald-400 font-semibold mb-1 block">▶ AI GENERATION PROMPT:</span>
                                {asset.prompt}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                      
                      {/* Master Overlay */}
                      <div className="absolute inset-0 pointer-events-none bg-[radial-gradient(ellipse_at_center,transparent_0%,rgba(0,0,0,0.8)_100%)]"></div>
                      <div className="relative z-10 text-center pointer-events-none w-full max-w-md mx-auto px-6">
                        <Activity size={48} className="mx-auto mb-4 text-indigo-400 animate-spin" />
                        <h3 className="text-xl font-bold text-white mb-2 shadow-black drop-shadow-md">Stitching in Progress...</h3>
                        <p className="text-sm text-slate-300 bg-black/60 px-4 py-1.5 rounded-full border border-white/10 backdrop-blur-md inline-flex items-center gap-2 mb-6">
                          <Layers size={14} className="text-indigo-400" />
                          Merging {generatedAssets.length} scene tracks
                        </p>
                        
                        {/* Progress Bar */}
                        <div className="w-full h-1.5 bg-white/10 rounded-full overflow-hidden shadow-inner backdrop-blur-md">
                          <div 
                            className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full transition-all duration-[2500ms] ease-linear"
                            style={{ width: `${Math.min(95, (activeStage / stages.length) * 100)}%` }}
                          ></div>
                        </div>
                        <div className="flex justify-between text-[10px] font-medium text-slate-400 mt-2 uppercase tracking-widest">
                          <span>Progress</span>
                          <span>{Math.round(Math.min(95, (activeStage / stages.length) * 100))}%</span>
                        </div>
                      </div>
                    </>
                  ) : (
                    <div className="text-center relative z-10 w-full max-w-md mx-auto px-6">
                      <Activity size={48} className="mx-auto mb-6 text-indigo-500 animate-pulse" />
                      <h3 className="text-xl font-medium text-white mb-2">
                        {aiQuestion ? 'Awaiting Clarification...' : 'Orchestrating Fleet...'}
                      </h3>
                      <p className="text-sm text-slate-400 mx-auto mb-8">
                        {aiQuestion 
                          ? 'The AI Director needs a bit more context before rolling cameras.'
                          : 'The AI fleet is preparing the execution graph and provisioning workers.'}
                      </p>
                      
                      {/* Initial Progress Bar */}
                      {!aiQuestion && (
                        <>
                          <div className="w-full h-1.5 bg-white/10 rounded-full overflow-hidden shadow-inner">
                            <div 
                              className="h-full bg-indigo-500 rounded-full transition-all duration-[2500ms] ease-linear"
                              style={{ width: `${Math.min(25, (activeStage / stages.length) * 100)}%` }}
                            ></div>
                          </div>
                          <div className="flex justify-between text-[10px] font-medium text-slate-500 mt-2 uppercase tracking-widest">
                            <span>Initializing</span>
                            <span>{Math.round(Math.min(25, (activeStage / stages.length) * 100))}%</span>
                          </div>
                        </>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Live Assets Grid from Redis */}
            <div className="p-6 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-xl shadow-2xl">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-2">
                  <Layers size={16} />
                  Live Asset Generation Feed (Redis Cache)
                </h2>
                <div className="flex items-center gap-2 text-xs text-emerald-400 bg-emerald-400/10 px-3 py-1 rounded-full border border-emerald-400/20">
                  <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></div>
                  Subscribed
                </div>
              </div>

              {currentPrompt && (
                <div className="mb-4 px-4 py-3 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-start gap-2 animate-in fade-in duration-300">
                  <Activity size={14} className="text-indigo-400 animate-spin mt-0.5 shrink-0" />
                  <p className="text-xs text-indigo-200 font-mono leading-relaxed">
                    <span className="text-indigo-400 font-semibold">Now rendering: </span>
                    {currentPrompt}
                  </p>
                </div>
              )}

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 min-h-[140px]">
                {generatedAssets.length === 0 ? (
                  <div className="col-span-full flex items-center justify-center text-slate-500 text-sm border border-dashed border-white/10 rounded-xl bg-black/20">
                    Assets will appear here in real-time as workers finish...
                  </div>
                ) : (
                  generatedAssets.map((asset, i) => (
                    <div key={asset.id} className="group relative aspect-video rounded-xl overflow-hidden border border-white/10 bg-black animate-in zoom-in fade-in duration-500">
                      {asset.type === 'video' ? (
                        <video
                          src={asset.url}
                          autoPlay
                          loop
                          muted
                          playsInline
                          className="w-full h-full object-cover opacity-60 group-hover:opacity-100 transition-opacity duration-300"
                        />
                      ) : (
                        <img src={asset.url} alt={asset.name} className="w-full h-full object-cover opacity-60 group-hover:opacity-100 transition-opacity duration-300" />
                      )}
                      <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent"></div>
                      <div className="absolute bottom-2 left-2 right-2">
                        <div className="flex items-center gap-1 text-xs text-white mb-1">
                          {asset.type === 'image' ? <ImageIcon size={12} className="text-blue-400"/> : 
                           asset.type === 'video' ? <Film size={12} className="text-purple-400" /> :
                           <Music size={12} className="text-emerald-400" />}
                          <span className="truncate">{asset.name}</span>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}
