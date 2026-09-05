import React from 'react';
import { 
  Radar, 
  Layers, 
  UserCheck, 
  Target, 
  Play, 
  Loader2,
  CheckCircle2,
  Activity
} from 'lucide-react';

const AGENT_ICONS = {
  scanner: Radar,
  classifier: Layers,
  profile: UserCheck,
  matcher: Target
};

const AGENT_COLORS = {
  scanner: 'from-blue-600 to-cyan-600 text-blue-600 bg-blue-50 border-blue-200',
  classifier: 'from-indigo-600 to-purple-600 text-indigo-600 bg-indigo-50 border-indigo-200',
  profile: 'from-purple-600 to-pink-600 text-purple-600 bg-purple-50 border-purple-200',
  matcher: 'from-emerald-600 to-teal-600 text-emerald-600 bg-emerald-50 border-emerald-200'
};

export default function AgentCard({ card, onRun, isRunning }) {
  const IconComponent = AGENT_ICONS[card.agent_id] || Activity;
  const colorTheme = AGENT_COLORS[card.agent_id] || 'from-slate-600 to-slate-800 text-slate-600 bg-slate-50 border-slate-200';

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs hover:shadow-md transition-all flex flex-col justify-between">
      <div>
        {/* Top Header */}
        <div className="flex items-center justify-between gap-3 mb-3">
          <div className="flex items-center gap-3">
            <div className={`w-11 h-11 rounded-xl flex items-center justify-center border shadow-xs ${colorTheme}`}>
              <IconComponent className="w-5 h-5" />
            </div>
            <div>
              <h4 className="font-bold text-navy-900 text-base">{card.name}</h4>
              <div className="flex items-center gap-1.5 text-xs text-slate-500">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                <span className="capitalize">{card.status}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Description */}
        <p className="text-xs text-slate-500 mb-4 leading-relaxed line-clamp-2">
          {card.description}
        </p>

        {/* Key Metric Box */}
        <div className="bg-slate-50 rounded-xl p-3 border border-slate-100 mb-4">
          <span className="text-[11px] font-medium text-slate-400 uppercase tracking-wider block">
            {card.metric_label}
          </span>
          <span className="text-lg font-extrabold text-navy-900 block mt-0.5">
            {card.metric_value}
          </span>
        </div>
      </div>

      {/* Action Button */}
      <button
        onClick={() => onRun(card.agent_id)}
        disabled={isRunning}
        className="w-full py-2.5 px-4 rounded-xl border border-slate-200 hover:border-slate-300 bg-white hover:bg-slate-50 text-slate-800 font-semibold text-xs flex items-center justify-center gap-2 transition-all shadow-2xs disabled:opacity-60"
      >
        {isRunning ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin text-brand-600" />
            <span>Executing Agent...</span>
          </>
        ) : (
          <>
            <Play className="w-3.5 h-3.5 text-brand-600 fill-brand-600" />
            <span>{card.action_label}</span>
          </>
        )}
      </button>
    </div>
  );
}
