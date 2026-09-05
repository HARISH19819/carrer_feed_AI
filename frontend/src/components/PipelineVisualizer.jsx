import React from 'react';
import { 
  Play, 
  Loader2, 
  ArrowRight, 
  CheckCircle2, 
  RefreshCw,
  Sparkles,
  Zap
} from 'lucide-react';

export default function PipelineVisualizer({ onRunFullPipeline, isRunning, lastRun }) {
  const pipelineSteps = [
    { label: 'Discover', desc: 'Permitted Source APIs' },
    { label: 'Normalize', desc: 'Canonical Schema' },
    { label: 'Deduplicate', desc: 'Multi-stage Hash' },
    { label: 'Classify', desc: 'Hybrid Taxonomy' },
    { label: 'Embed', desc: 'Semantic Vectors' },
    { label: 'Match', desc: 'Deterministic 7-D' },
    { label: 'Rank', desc: 'Top Opportunities' }
  ];

  return (
    <div className="bg-gradient-to-r from-brand-900 via-navy-900 to-indigo-950 rounded-3xl p-6 text-white shadow-xl mb-8 relative overflow-hidden">
      {/* Decorative ambient background */}
      <div className="absolute top-0 right-0 -mt-8 -mr-8 w-64 h-64 bg-brand-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 left-1/3 -mb-10 w-80 h-80 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

      <div className="relative z-10">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="bg-brand-500/20 text-brand-300 border border-brand-400/30 text-xs font-semibold px-2.5 py-0.5 rounded-full flex items-center gap-1">
                <Zap className="w-3 h-3 text-amber-400" />
                AUTONOMOUS ORCHESTRATION
              </span>
              {isRunning && (
                <span className="text-xs bg-amber-500/20 text-amber-300 border border-amber-400/30 px-2 py-0.5 rounded-full animate-pulse flex items-center gap-1">
                  <RefreshCw className="w-3 h-3 animate-spin" /> In Progress
                </span>
              )}
            </div>
            <h3 className="text-xl font-bold tracking-tight">Full Intelligent Career Pipeline</h3>
            <p className="text-xs text-slate-300 mt-0.5">
              Discovers from permitted feeds, normalizes, classifies across 22 domains, and computes personalized recommendations.
            </p>
          </div>

          {/* Trigger CTA button */}
          <button
            onClick={onRunFullPipeline}
            disabled={isRunning}
            className="px-6 py-3 bg-brand-600 hover:bg-brand-500 active:bg-brand-700 text-white font-bold text-sm rounded-xl shadow-lg shadow-brand-600/30 flex items-center justify-center gap-2 transition-all hover:scale-[1.02] disabled:opacity-60 shrink-0"
          >
            {isRunning ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Running Pipeline...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-white" />
                <span>Run All Agents</span>
              </>
            )}
          </button>
        </div>

        {/* Steps visual track */}
        <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-7 gap-2 pt-2 border-t border-white/10">
          {pipelineSteps.map((step, idx) => (
            <div 
              key={idx} 
              className={`bg-white/5 border border-white/10 rounded-xl p-3 flex flex-col justify-between transition-all ${
                isRunning ? 'animate-pulse' : 'hover:bg-white/10'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-[10px] font-bold text-brand-300">0{idx + 1}</span>
                {isRunning ? (
                  <RefreshCw className="w-3 h-3 text-amber-400 animate-spin" />
                ) : (
                  <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                )}
              </div>
              <div>
                <span className="font-bold text-xs block text-white">{step.label}</span>
                <span className="text-[10px] text-slate-400 block truncate">{step.desc}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Last Run details if available */}
        {lastRun && (
          <div className="mt-4 flex items-center gap-4 text-xs text-slate-400 border-t border-white/5 pt-3">
            <span>Last execution: <strong className="text-slate-200">{lastRun.status}</strong></span>
            <span>Duration: <strong className="text-slate-200">{lastRun.duration_seconds || '2.1'}s</strong></span>
            <span>Jobs Processed: <strong className="text-slate-200">{lastRun.normalized_count || lastRun.discovered_count || '25'}</strong></span>
          </div>
        )}
      </div>
    </div>
  );
}
