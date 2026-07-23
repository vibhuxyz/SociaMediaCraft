import { useState } from 'react';
import { Loader2, CheckCircle2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { uploadImage, checkJobStatus, type JobStatus } from '../../../services/v0';

export function V0Page() {
  const [file, setFile] = useState<File | null>(null);
  const [v0Status, setV0Status] = useState<JobStatus | null>(null);
  const [v0Loading, setV0Loading] = useState(false);

  const handleV0Submit = async () => {
    if (!file) return;
    setV0Loading(true);
    try {
      const { jobId } = await uploadImage(file);
      setV0Status({ id: jobId, status: 'queued' });
      
      const interval = setInterval(async () => {
        const status = await checkJobStatus(jobId);
        setV0Status(status);
        if (status.status === 'completed' || status.status === 'failed') {
          clearInterval(interval);
          setV0Loading(false);
        }
      }, 1500);
    } catch (e) {
      console.error(e);
      setV0Loading(false);
    }
  };

  return (
    <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-slate-900">Version 0: AI Infrastructure Foundation</h2>
        <p className="text-slate-500 mt-1">Test file uploads, job queues (BullMQ), PostgreSQL, and worker status.</p>
      </div>
      
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
        <div className="mb-4">
          <label className="block text-sm font-medium text-slate-700 mb-2">Upload Test Image</label>
          <input 
            type="file" 
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
          />
        </div>
        <Button onClick={handleV0Submit} disabled={!file || v0Loading}>
          {v0Loading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
          Create AI Job
        </Button>

        {v0Status && (
          <div className="mt-6 p-4 bg-slate-50 rounded-lg border border-slate-100">
            <h3 className="font-semibold text-slate-800 mb-3">Job Status</h3>
            <div className="flex items-center gap-3 text-sm">
              <span className="font-mono text-slate-500">{v0Status.id}</span>
              <span className={`px-2.5 py-1 rounded-full text-xs font-medium capitalize ${
                v0Status.status === 'completed' ? 'bg-green-100 text-green-700' :
                v0Status.status === 'processing' ? 'bg-blue-100 text-blue-700' :
                'bg-amber-100 text-amber-700'
              }`}>
                {v0Status.status}
              </span>
            </div>
            {v0Status.status === 'completed' && (
              <div className="mt-3 text-sm text-indigo-600 flex items-center gap-1">
                <CheckCircle2 className="w-4 h-4" /> Uploaded to R2/S3 Successfully
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
