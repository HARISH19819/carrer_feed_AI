import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { TrendingUp, Award, BookOpen, AlertCircle, Sparkles, CheckCircle2 } from 'lucide-react';

export default function SkillGapsPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchGaps = async () => {
      try {
        const res = await api.getSkillGaps();
        setData(res);
      } catch (err) {
        console.error('Error fetching skill gaps:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchGaps();
  }, []);

  const getImportanceBadge = (imp) => {
    if (imp === 'Critical') return 'bg-rose-50 text-rose-700 border-rose-200';
    if (imp === 'High Impact') return 'bg-amber-50 text-amber-700 border-amber-200';
    return 'bg-blue-50 text-blue-700 border-blue-200';
  };

  return (
    <div className="max-w-6xl mx-auto py-8 px-4 sm:px-6 lg:px-8 space-y-8">
      
      {/* Header */}
      <div>
        <div className="flex items-center gap-2">
          <TrendingUp className="w-6 h-6 text-brand-600" />
          <h1 className="text-3xl font-extrabold text-navy-900">Career Skill Gap Intelligence</h1>
        </div>
        <p className="text-xs text-slate-500 mt-1">
          Analyzed across your top matching opportunities to highlight the highest-ROI skills to learn next
        </p>
      </div>

      {/* Recommended Next Focus Card */}
      {data?.top_recommended_next && (
        <div className="bg-gradient-to-r from-brand-700 via-indigo-700 to-navy-900 rounded-3xl p-6 text-white shadow-xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <span className="text-xs font-bold uppercase tracking-wider text-brand-300 flex items-center gap-1">
              <Sparkles className="w-3.5 h-3.5 text-amber-400" />
              Highest Strategic Impact
            </span>
            <h3 className="text-2xl font-black">Learn {data.top_recommended_next} Next</h3>
            <p className="text-xs text-slate-300 max-w-xl">
              Acquiring this skill will significantly increase your compatibility score across more than half of your targeted career opportunities.
            </p>
          </div>
          <div className="bg-white/10 px-4 py-2.5 rounded-2xl border border-white/20 text-center shrink-0">
            <span className="text-[10px] uppercase font-bold text-slate-300 block">Candidate Profile</span>
            <span className="text-sm font-bold text-emerald-400 flex items-center gap-1 mt-0.5">
              <CheckCircle2 className="w-4 h-4" /> {data.candidate_skills_count} Skills Active
            </span>
          </div>
        </div>
      )}

      {/* Skill Gaps List */}
      <div className="bg-white rounded-3xl border border-slate-200 p-6 shadow-xs space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <h3 className="font-bold text-navy-900 text-lg">Top Missing Requirements in Your Feed</h3>
          <span className="text-xs text-slate-400">
            Based on {data?.total_matches_analyzed || 0} analyzed matching opportunities
          </span>
        </div>

        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3, 4].map(n => (
              <div key={n} className="h-20 bg-slate-100 rounded-2xl animate-pulse" />
            ))}
          </div>
        ) : data?.skill_gaps?.length > 0 ? (
          <div className="space-y-3">
            {data.skill_gaps.map((gap, idx) => (
              <div 
                key={idx} 
                className="bg-slate-50/60 rounded-2xl p-4 border border-slate-200/80 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:border-slate-300 transition-colors"
              >
                <div className="space-y-1.5 flex-1">
                  <div className="flex items-center gap-2">
                    <h4 className="font-extrabold text-navy-900 text-base">{gap.skill}</h4>
                    <span className={`text-xs font-bold px-2.5 py-0.5 rounded-full border ${getImportanceBadge(gap.importance)}`}>
                      {gap.importance}
                    </span>
                    <span className="text-xs text-slate-500 font-medium">
                      Required by {gap.jobs_requiring} matching roles
                    </span>
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed">
                    <strong className="text-slate-800">Why learn this:</strong> {gap.why_learn_this}
                  </p>
                </div>

                {/* Progress Demand Gauge */}
                <div className="w-full md:w-48 shrink-0 space-y-1">
                  <div className="flex justify-between text-xs font-semibold text-slate-600">
                    <span>Demand in Feed</span>
                    <span className="font-bold text-navy-900">{gap.demand_percentage}%</span>
                  </div>
                  <div className="h-2 w-full bg-slate-200 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-brand-600 rounded-full"
                      style={{ width: `${gap.demand_percentage}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-8 text-center text-slate-500 text-sm">
            No skill gaps found. Your profile matches all requirements in the current recommendations!
          </div>
        )}
      </div>

    </div>
  );
}
