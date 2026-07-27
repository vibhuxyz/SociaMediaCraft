import React, { useRef, useState } from 'react';
import { Terminal, UploadCloud, Play, Activity, MessageSquare, Send, X, Image as ImageIcon, Film } from 'lucide-react';

interface DirectorPromptProps {
  initialPrompt?: string;
  isGenerating: boolean;
  onGenerate: (prompt: string, files: File[]) => void;
  aiQuestion?: { question: string; options?: string[] } | null;
  onAnswerSubmit?: (answer: string) => void;
}

export function DirectorPrompt({ 
  initialPrompt = '', 
  isGenerating, 
  onGenerate,
  aiQuestion = null,
  onAnswerSubmit
}: DirectorPromptProps) {
  const [prompt, setPrompt] = useState(initialPrompt);
  const [files, setFiles] = useState<File[]>([]);
  const [aiAnswer, setAiAnswer] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files);
      setFiles(prev => [...prev, ...newFiles]);
    }
  };

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmitAnswer = () => {
    if (onAnswerSubmit && aiAnswer) {
      onAnswerSubmit(aiAnswer);
      setAiAnswer('');
    }
  };

  return (
    <div className="p-6 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-xl shadow-2xl relative overflow-hidden group">
      <div className="absolute inset-0 bg-gradient-to-br from-white/[0.02] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
      
      <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
        <Terminal size={18} className="text-indigo-400" />
        Director's Prompt
      </h2>

      {/* Dynamic AI Clarification Box OR Standard Input */}
      {aiQuestion ? (
        <div className="bg-indigo-950/40 border border-indigo-500/30 p-4 rounded-xl mb-6 backdrop-blur-md animate-in fade-in zoom-in duration-300">
          <h3 className="text-sm font-medium text-indigo-300 mb-2 flex items-center gap-2">
            <MessageSquare size={14} /> AI Clarification Needed
          </h3>
          <p className="text-white text-sm mb-4 leading-relaxed">{aiQuestion.question}</p>
          
          {aiQuestion.options ? (
            <div className="space-y-2 mb-4">
              {aiQuestion.options.map((opt, i) => (
                <button 
                  key={i}
                  onClick={() => setAiAnswer(opt)}
                  className={`w-full text-left px-4 py-3 rounded-lg text-sm transition-all ${
                    aiAnswer === opt ? 'bg-indigo-500 text-white' : 'bg-white/5 text-slate-300 hover:bg-white/10'
                  }`}
                >
                  {opt}
                </button>
              ))}
            </div>
          ) : (
            <input 
              type="text" 
              value={aiAnswer}
              onChange={(e) => setAiAnswer(e.target.value)}
              className="w-full bg-black/40 border border-white/10 rounded-lg px-4 py-3 text-sm text-white focus:ring-2 focus:ring-indigo-500 outline-none mb-4"
              placeholder="Type your answer..."
            />
          )}
          
          <button 
            onClick={handleSubmitAnswer}
            disabled={!aiAnswer}
            className="w-full py-3 rounded-lg bg-indigo-500 text-white font-medium hover:bg-indigo-600 disabled:opacity-50 transition-colors flex items-center justify-center gap-2"
          >
            <Send size={16} /> Submit Answer
          </button>
        </div>
      ) : (
        <>
          <textarea 
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="w-full h-28 p-4 rounded-xl bg-black/40 border border-white/10 text-slate-200 placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500/50 transition-all resize-none mb-4 text-sm leading-relaxed"
            placeholder="Describe your scene..."
          />
          
          {/* Upload References Dropzone */}
          <div 
            onClick={() => fileInputRef.current?.click()}
            className="border border-dashed border-white/20 bg-white/[0.02] hover:bg-white/[0.05] transition-colors rounded-xl p-4 mb-4 flex flex-col items-center justify-center text-center cursor-pointer group/dropzone"
          >
            <input 
              type="file" 
              ref={fileInputRef} 
              className="hidden" 
              multiple 
              accept="image/*,video/*" 
              onChange={handleFileChange} 
            />
            <div className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center mb-2 group-hover/dropzone:scale-110 transition-transform">
              <UploadCloud size={18} className="text-slate-400 group-hover/dropzone:text-indigo-400" />
            </div>
            <p className="text-xs font-medium text-slate-300">Add Image/Video References</p>
            <p className="text-[10px] text-slate-500 mt-1">Drag & drop or click to upload</p>
          </div>

          {/* Selected Files Preview */}
          {files.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-6">
              {files.map((file, idx) => (
                <div key={idx} className="relative group bg-white/10 border border-white/10 rounded-lg p-2 flex items-center gap-2 pr-8 text-xs text-slate-300 max-w-[200px]">
                  {file.type.startsWith('video') ? <Film size={14} className="text-purple-400 shrink-0" /> : <ImageIcon size={14} className="text-blue-400 shrink-0" />}
                  <span className="truncate">{file.name}</span>
                  <button 
                    onClick={(e) => { e.stopPropagation(); removeFile(idx); }}
                    className="absolute right-2 text-slate-400 hover:text-white"
                  >
                    <X size={14} />
                  </button>
                </div>
              ))}
            </div>
          )}

          <button 
            onClick={() => onGenerate(prompt, files)}
            disabled={isGenerating || (!prompt.trim() && files.length === 0)}
            className="w-full py-4 rounded-xl bg-white text-black font-semibold hover:bg-slate-200 transition-all duration-300 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed group relative overflow-hidden"
          >
            {isGenerating ? (
              <>
                <Activity size={18} className="animate-spin text-indigo-600" />
                Analyzing...
              </>
            ) : (
              <>
                <Play size={18} className="fill-current group-hover:scale-110 transition-transform" />
                Action!
              </>
            )}
          </button>
        </>
      )}
    </div>
  );
}
