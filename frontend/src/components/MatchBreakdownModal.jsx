import React from 'react';
import { 
  X, 
  Building2, 
  MapPin, 
  Clock, 
  ExternalLink, 
  CheckCircle, 
  AlertCircle, 
  BarChart3, 
  ShieldAlert,
  Bookmark,
  BookmarkCheck,
  CheckCircle2
} from 'lucide-react';

export default function MatchBreakdownModal({ 
  job, 
  matchData, 
  isOpen, 
  onClose, 
  onApplyClick, 
  onSave, 
  onUnsave,
  isSaved
}) {
  if (!isOpen || !job) return null;

  const breakdown = matchData?.breakdown || {};
  const score = matchData?.score;
  const matchTier = matchData?.match_tier || 'Good Match';
  const strongMatches = matchData?.strong_matches || [];
  const missingSkills = matchData?.missing_skills || [];
  const whyMatched = matchData?.why_matched || 'Matches your career profile.';

  const dimensions = [
    { label: 'Skills Match (30% weight)', value: breakdown.skill_score || 0, color: 'bg-emerald-500' },
    { label: 'Role Alignment (20% weight)', value: breakdown.role_score || 0, color: 'bg-blue-500' },
    { label: 'Domain Fit (15% weight)', value: breakdown.domain_score || 0, color: 'bg-indigo-500' },
    { label: 'Experience Match (15% weight)', value: breakdown.experience_score || 0, color: 'bg-purple-500' },
    { label: 'Education Match (10% weight)', value: breakdown.education_score || 0, color: 'bg-teal-500' },
    { label: 'Location Match (5% weight)', value: breakdown.location_score || 0, color: 'bg-amber-500' },
    { label: 'Preferences (5% weight)', value: breakdown.preference_score || 0, color: 'bg-rose-500' },
    { label: 'Semantic Similarity', value: breakdown.semantic_similarity || 0, color: 'bg-sky-500' },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs overflow-y-auto animate-fadeIn">
      <div className="bg-white rounded-3xl max-w-2xl w-full max-h-[90vh] flex flex-col shadow-2xl border border-slate-200 overflow-hidden">
        
        {/* Modal Header */}
        <div className="p-6 border-b border-slate-100 flex items-start justify-between gap-4 bg-slate-50/50">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <span className="text-xs font-semibold text-brand-700 bg-brand-50 px-2.5 py-0.5 rounded-full border border-brand-200">
                {job.domain || 'Software Development'}
              </span>
              <span className="text-xs text-slate-400">•</span>
              <span className="text-xs text-slate-600 font-medium capitalize">{job.employment_type?.replace('_', ' ')}</span>
            </div>
            <h2 className="text-2xl font-bold text-navy-900">{job.title}</h2>
            <div className="flex items-center gap-4 text-xs text-slate-500 mt-2 flex-wrap">
              <span className="flex items-center gap-1 font-semibold text-slate-700">
                <Building2 className="w-3.5 h-3.5 text-slate-400" />
                {job.company}
              </span>
              <span className="flex items-center gap-1">
                <MapPin className="w-3.5 h-3.5 text-slate-400" />
                {job.location} ({job.location_type})
              </span>
              <span className="flex items-center gap-1">
                <Clock className="w-3.5 h-3.5 text-slate-400" />
                Exp: {job.experience_required}
              </span>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-200 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6">
          
          {/* Match Score & Transparent Explanation */}
          {score !== undefined && (
            <div className="bg-gradient-to-br from-brand-50/60 to-indigo-50/40 rounded-2xl p-5 border border-brand-100">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="w-14 h-14 rounded-2xl bg-brand-600 text-white flex flex-col items-center justify-center font-black shadow-md shadow-brand-500/30">
                    <span className="text-xl leading-none">{score}%</span>
                    <span className="text-[8px] uppercase tracking-wider opacity-80">Match</span>
                  </div>
                  <div>
                    <h4 className="font-bold text-navy-900 text-base">{matchTier}</h4>
                    <p className="text-xs text-slate-600">Deterministic multi-dimensional compatibility calculation</p>
                  </div>
                </div>
                <span className="text-xs font-semibold px-2.5 py-1 bg-white border border-brand-200 text-brand-700 rounded-lg shadow-xs">
                  Transparent AI
                </span>
              </div>

              {/* Narrative explanation */}
              <div className="text-xs text-slate-700 bg-white/90 p-3 rounded-xl border border-brand-100/80 mb-3 leading-relaxed">
                <strong className="text-brand-800 font-semibold block mb-1">Why this role fits you:</strong>
                {whyMatched}
              </div>

              {/* Skills matched & missing */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
                <div className="bg-white/80 p-3 rounded-xl border border-emerald-200">
                  <span className="text-xs font-bold text-emerald-800 flex items-center gap-1 mb-2">
                    <CheckCircle className="w-3.5 h-3.5 text-emerald-600" />
                    Matching Skills ({strongMatches.length})
                  </span>
                  <div className="flex flex-wrap gap-1">
                    {strongMatches.length > 0 ? (
                      strongMatches.map((s, i) => (
                        <span key={i} className="text-[11px] font-medium bg-emerald-50 text-emerald-800 px-2 py-0.5 rounded border border-emerald-200">
                          ✓ {s}
                        </span>
                      ))
                    ) : (
                      <span className="text-xs text-slate-400">None explicitly listed</span>
                    )}
                  </div>
                </div>

                <div className="bg-white/80 p-3 rounded-xl border border-slate-200">
                  <span className="text-xs font-bold text-slate-700 flex items-center gap-1 mb-2">
                    <AlertCircle className="w-3.5 h-3.5 text-amber-500" />
                    Missing Skills ({missingSkills.length})
                  </span>
                  <div className="flex flex-wrap gap-1">
                    {missingSkills.length > 0 ? (
                      missingSkills.map((m, i) => (
                        <span key={i} className="text-[11px] font-medium bg-slate-100 text-slate-700 px-2 py-0.5 rounded">
                          • {m}
                        </span>
                      ))
                    ) : (
                      <span className="text-xs text-emerald-600 font-medium">No critical gaps!</span>
                    )}
                  </div>
                </div>
              </div>

              {/* 7-Dimension Score Progress Bars */}
              <div className="mt-4 pt-4 border-t border-brand-100">
                <h5 className="text-xs font-bold text-navy-900 mb-2.5 flex items-center gap-1.5">
                  <BarChart3 className="w-4 h-4 text-brand-600" />
                  Detailed Dimension Breakdown
                </h5>
                <div className="space-y-2">
                  {dimensions.map((d, idx) => (
                    <div key={idx} className="flex items-center text-xs">
                      <span className="w-48 text-slate-600 font-medium truncate">{d.label}</span>
                      <div className="flex-1 h-2 bg-slate-200 rounded-full overflow-hidden mx-3">
                        <div 
                          className={`h-full ${d.color} rounded-full transition-all duration-500`}
                          style={{ width: `${Math.min(100, Math.max(5, d.value))}%` }}
                        />
                      </div>
                      <span className="w-10 text-right font-bold text-slate-700">{Math.round(d.value)}%</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Job Description */}
          <div>
            <h4 className="font-bold text-navy-900 text-sm uppercase tracking-wider mb-2">Job Description</h4>
            <div className="text-sm text-slate-600 leading-relaxed whitespace-pre-line bg-slate-50 p-4 rounded-2xl border border-slate-200 max-h-60 overflow-y-auto">
              {job.description}
            </div>
          </div>

          {/* Transparent Disclaimer */}
          <div className="flex items-start gap-2 p-3 bg-amber-50/70 border border-amber-200 rounded-xl text-amber-900 text-[11px]">
            <ShieldAlert className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
            <p>
              <strong>Evaluation Disclaimer:</strong> Compatibility scores estimate algorithmic alignment between the employer requirements and your extracted resume profile. It does not guarantee employment or predict hiring decisions.
            </p>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="p-5 border-t border-slate-100 bg-slate-50 flex items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <button
              onClick={() => isSaved ? onUnsave(job.id) : onSave(job.id)}
              className={`px-4 py-2.5 rounded-xl border text-sm font-semibold flex items-center gap-1.5 transition-colors ${
                isSaved
                  ? 'bg-amber-50 border-amber-300 text-amber-800'
                  : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-100'
              }`}
            >
              {isSaved ? <BookmarkCheck className="w-4 h-4 text-amber-600" /> : <Bookmark className="w-4 h-4 text-slate-400" />}
              <span>{isSaved ? 'Saved in List' : 'Save Job'}</span>
            </button>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-xs text-slate-500 hidden sm:inline">
              Verified Source: <strong className="text-slate-800">{job.source}</strong>
            </span>
            <a
              href={job.application_url || job.source_url}
              target="_blank"
              rel="noopener noreferrer"
              onClick={() => onApplyClick && onApplyClick(job.id)}
              className="flex items-center gap-2 px-6 py-2.5 bg-brand-600 hover:bg-brand-700 text-white font-semibold text-sm rounded-xl shadow-md shadow-brand-500/20 transition-all hover:scale-[1.02]"
            >
              <span>Apply on Original Source</span>
              <ExternalLink className="w-4 h-4" />
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
