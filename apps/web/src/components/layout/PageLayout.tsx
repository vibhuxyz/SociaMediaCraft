import { NavLink, Outlet } from 'react-router-dom';
import { Upload, FileVideo, GitMerge, Wrench, BrainCircuit, Play } from 'lucide-react';

export function PageLayout() {
  const tabs = [
    { path: '/v0', title: 'V0: Infrastructure', icon: <Upload className="w-4 h-4" /> },
    { path: '/v1', title: 'V1: Planning Engine', icon: <BrainCircuit className="w-4 h-4" /> },
    { path: '/v2', title: 'V2: Workflow Engine', icon: <GitMerge className="w-4 h-4" /> },
    { path: '/v3', title: 'V3: Tool Calling', icon: <Wrench className="w-4 h-4" /> },
    { path: '/v4', title: 'V4: Video Gen', icon: <FileVideo className="w-4 h-4" /> },
  ];

  return (
    <div className="flex h-screen bg-slate-50 font-sans">
      {/* Sidebar */}
      <div className="w-64 bg-slate-900 text-white flex flex-col">
        <div className="p-6 border-b border-slate-800">
          <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <Play className="w-5 h-5 text-indigo-400 fill-current" />
            Omni AI Platform
          </h1>
          <p className="text-slate-400 text-xs mt-1">Test Dashboard</p>
        </div>
        <div className="flex-1 overflow-y-auto py-4">
          <nav className="space-y-1 px-3">
            {tabs.map((tab) => (
              <NavLink
                key={tab.path}
                to={tab.path}
                className={({ isActive }) =>
                  `w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-indigo-600 text-white'
                      : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                  }`
                }
              >
                {tab.icon}
                {tab.title}
              </NavLink>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto p-8">
          <Outlet />
        </div>
      </div>
    </div>
  );
}
