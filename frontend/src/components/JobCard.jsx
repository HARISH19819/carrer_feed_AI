import React from 'react';
import { 
  Building2, 
  MapPin, 
  Briefcase, 
  Clock, 
  Check, 
  AlertCircle, 
  ExternalLink, 
  Bookmark, 
  BookmarkCheck,
  CheckCircle2,
  ChevronRight,
  Info
} from 'lucide-react';

export default function JobCard({ 
  job, 
  matchScore, 
  matchTier, 
  strongMatches = [], 
  missingSkills = [], 
  whyMatched, 
  isSaved, 
  onSave, 
  onUnsave, 
  onApplyClick, 
  onViewDetails 
}) {
  const getScoreColor = (score) => {
    if (score >= 90) return { bg: 'bg-emerald-50 text-emerald-700 border-emerald-300', text: 'text-emerald-700', badge: 'bg-emerald-100 text-emerald-800' };
    if (score >= 80) return { bg: 'bg-blue-50 text-blue-700 border-blue-300', text: 'text-blue-700', badge: 'bg-blue-100 text-blue-800' };
    if (score >= 70) return { bg: 'bg-indigo-50 text-indigo-700 border-indigo-300', text: 'text-indigo-700', badge: 'bg-indigo-100 text-indigo-800' };
    if (score >= 60) return { bg: 'bg-amber-50 text-amber-700 border-amber-300', text: 'text-amber-700', badge: 'bg-amber-100 text-amber-800' };
    return { bg: 'bg-slate-50 text-slate-700 border-slate-300', text: 'text-slate-600', badge: 'bg-slate-100 text-slate-700' };
  };

  const scoreTheme = matchScore !== undefined ? getScoreColor(matchScore) : null;

  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm hover:shadow-md hover:border-slate-300 transition-all p-5 flex flex-col justify-between group">
      <div>
        {/* Top bar: Company & Score Badge */}
        <div className="flex items-start justify-between gap-4 mb-3">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-semibold text-brand-700 uppercase tracking-wider bg-brand-50 px-2.5 py-0.5 rounded-md border border-brand-100">
                {job.domain || 'Software'}
              </span>
              <span className="text-xs text-slate-400">•</span>
              <span className="text-xs text-slate-500 capitalize">{job.employment_type?.replace('_', ' ')}</span>
            </div>
            <h3 
              onClick={() => onViewDetails && onViewDetails(job)}
              className="text-lg font-bold text-navy-900 hover:text-brand-600 cursor-pointer transition-colors leading-snug line-clamp-1"
              title={job.title}
            >
              {job.title}
            </h3>
            <div className="flex items-center gap-3 text-xs text-slate-500 mt-1 flex-wrap">
              <span className="flex items-center gap-1 font-medium text-slate-700">
                <Building2 className="w-3.5 h-3.5 text-slate-400" />
                {job.company}
              </span>
              <span className="flex items-center gap-1">
                <MapPin className="w-3.5 h-3.5 text-slate-400" />
                {job.location}
              </span>
              <span className="flex items-center gap-1">
                <Clock className="w-3.5 h-3.5 text-slate-400" />
                {job.relative_posted_time || 'Recent'}
              </span>
            </div>
          </div>

          {/* Prominent Match Score */}
          {matchScore !== undefined && (
            <div className="flex flex-col items-end shrink-0">
              <div className={`px-3 py-1.5 rounded-xl border text-center font-bold tracking-tight shadow-xs ${scoreTheme.bg}`}>
                <span className="text-xl font-extrabold">{matchScore}%</span>
                <span className="block text-[9px] uppercase font-semibold tracking-wider opacity-90">MATCH</span>
              </div>
              {matchTier && (
                <span className={`mt-1 text-[10px] font-semibold px-2 py-0.5 rounded-full ${scoreTheme.badge}`}>
                  {matchTier}
                </span>
              )}
            </div>
          )}
        </div>

        {/* Experience & Source Pill */}
        <div className="flex items-center gap-2 mb-3 text-xs flex-wrap">
          <span className="bg-slate-100 text-slate-700 px-2 py-0.5 rounded font-medium">
            Exp: {job.experience_required || 'Fresher'}
          </span>
          {job.salary && job.salary !== 'Not specified' && (
            <span className="bg-emerald-50 text-emerald-800 border border-emerald-100 px-2 py-0.5 rounded font-medium">
              {job.salary}
            </span>
          )}
          <span className="text-[11px] text-slate-400 ml-auto flex items-center gap-1">
            Source: <strong className="text-slate-600 font-semibold">{job.source}</strong>
          </span>
        </div>

        {/* Matching & Missing Skills Chips */}
        <div className="space-y-2 mb-3 pt-2 border-t border-slate-100">
          {strongMatches.length > 0 && (
            <div className="flex items-center gap-1.5 flex-wrap">
              <span className="text-[11px] font-semibold text-emerald-700 flex items-center gap-0.5 mr-1">
                <Check className="w-3 h-3" /> Matches:
              </span>
              {strongMatches.slice(0, 4).map((s, idx) => (
                <span key={idx} className="bg-emerald-50 text-emerald-800 border border-emerald-200 text-[11px] font-medium px-2 py-0.5 rounded-md flex items-center gap-1">
                  ✓ {s}
                </span>
              ))}
              {strongMatches.length > 4 && (
                <span className="text-[11px] text-emerald-600 font-medium">+{strongMatches.length - 4} more</span>
              )}
            </div>
          )}

          {missingSkills.length > 0 && (
            <div className="flex items-center gap-1.5 flex-wrap">
              <span className="text-[11px] font-semibold text-slate-500 flex items-center gap-0.5 mr-1">
                <AlertCircle className="w-3 h-3 text-amber-500" /> Missing:
              </span>
              {missingSkills.slice(0, 3).map((m, idx) => (
                <span key={idx} className="bg-slate-100 text-slate-700 text-[11px] font-medium px-2 py-0.5 rounded-md">
                  • {m}
                </span>
              ))}
            </div>
          )}

          {/* Why matched snippet */}
          {whyMatched && (
            <p className="text-xs text-slate-500 bg-slate-50 p-2 rounded-lg border border-slate-100 italic line-clamp-2">
              "{whyMatched}"
            </p>
          )}
        </div>
      </div>

      {/* Bottom Actions */}
      <div className="pt-3 border-t border-slate-100 flex items-center justify-between gap-2 mt-2">
        <div className="flex items-center gap-2">
          {/* Save Button */}
          <button
            onClick={() => isSaved ? onUnsave && onUnsave(job.id) : onSave && onSave(job.id)}
            className={`p-2 rounded-lg border text-xs font-semibold flex items-center gap-1 transition-colors ${
              isSaved 
                ? 'bg-amber-50 border-amber-200 text-amber-700 hover:bg-amber-100' 
                : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50 hover:text-slate-900'
            }`}
            title={isSaved ? "Saved in your list" : "Save for later"}
          >
            {isSaved ? <BookmarkCheck className="w-4 h-4 text-amber-600" /> : <Bookmark className="w-4 h-4 text-slate-400" />}
            <span className="hidden sm:inline">{isSaved ? 'Saved' : 'Save'}</span>
          </button>

          {/* Details / Score Breakdown */}
          {onViewDetails && (
            <button
              onClick={() => onViewDetails(job)}
              className="px-3 py-2 rounded-lg border border-slate-200 hover:border-slate-300 text-slate-700 hover:bg-slate-50 text-xs font-semibold flex items-center gap-1 transition-colors"
            >
              <Info className="w-3.5 h-3.5 text-slate-400" />
              <span>Details</span>
            </button>
          )}
        </div>

        {/* External Apply */}
        <div className="flex items-center gap-2">
          <a
            href={job.application_url || job.source_url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={() => onApplyClick && onApplyClick(job.id)}
            className="flex items-center gap-1.5 px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold rounded-lg shadow-sm shadow-brand-500/20 transition-all hover:scale-[1.02]"
          >
            <span>Apply on Source</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>
      </div>
    </div>
  );
}
