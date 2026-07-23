import { useState } from 'react';
import { Loader2, Play, FileVideo } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { generateVideo, type VideoOutput } from '../../../services/v4';

export function V4Page() {
  const [v4Prompt, setV4Prompt] = useState('Generate a 60-second AI advertisement with cinematic camera motion.');
  const [v4Video, setV4Video] = useState<VideoOutput | null>(null);
  const [v4Loading, setV4Loading] = useState(false);

  const handleV4Submit = async () => {
    setV4Loading(true);
    try {
      const video = await generateVideo(v4Prompt);
      setV4Video(video);
    } finally {
      setV4Loading(false);
    }
  };

  return (
    <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-slate-900">Version 4: Video Generation</h2>
        <p className="text-slate-500 mt-1">Test the final FFmpeg render and scene merging pipeline.</p>
      </div>
      
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
        <div className="mb-4">
          <label className="block text-sm font-medium text-slate-700 mb-2">Video Prompt</label>
          <textarea 
            rows={3}
            value={v4Prompt}
            onChange={(e) => setV4Prompt(e.target.value)}
            className="w-full p-3 border border-slate-300 rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none resize-none"
          />
        </div>
        <Button onClick={handleV4Submit} disabled={v4Loading} className="w-full sm:w-auto bg-green-600 hover:bg-green-700">
          {v4Loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Play className="w-4 h-4 mr-2 fill-current" />}
          Generate AI Video
        </Button>

        {v4Video && (
          <div className="mt-6 border border-slate-200 rounded-xl overflow-hidden shadow-sm">
            <div className="aspect-video bg-slate-900 flex flex-col items-center justify-center text-slate-400 relative">
              <FileVideo className="w-12 h-12 mb-3 opacity-50" />
              <p>Video Rendered Successfully</p>
              <div className="absolute bottom-4 right-4 bg-black/60 px-2 py-1 rounded text-xs text-white">
                {v4Video.duration} • {v4Video.scenes} Scenes
              </div>
            </div>
            <div className="p-4 bg-white flex justify-between items-center">
              <div className="text-sm">
                <p className="font-semibold text-slate-800">Final Output</p>
                <a href={v4Video.url} className="text-indigo-600 hover:underline">{v4Video.url}</a>
              </div>
              <Button variant="outline" size="sm">Download MP4</Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
