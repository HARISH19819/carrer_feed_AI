import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import JobCard from '../components/JobCard';
import MatchBreakdownModal from '../components/MatchBreakdownModal';
import { Target, Sliders, CheckCircle2, FolderOpen } from 'lucide-react';

export default function MyMatchesPage() {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTier, setActiveTier] = useState('all');
  const [sortBy, setSortBy] = useState('score_desc');

  const [selectedJob, setSelectedJob] = useState(null);
  const [selectedMatchData, setSelectedMatchData] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState(null);

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  const fetchMatches = async () => {
    setLoading(true);
    try {
      const res = await api.getMatches({
        tier: activeTier,
        sort_by: sortBy,
        page_size: 30
      });
      setMatches(res.items || []);
    } catch (err) {
      console.error('Error fetching matches:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMatches();
  }, [activeTier, sortBy]);

  const handleSave = async (jobId) => {
    try {
      await api.saveJob(jobId);
      showToast('Saved to your collection.');
      setMatches(prev => prev.map(m => m.job_id === jobId ? { ...m, is_saved: true } : m));
    } catch {
      showToast('Could not save.');
    }
  };

  const handleUnsave = async (jobId) => {
    try {
      await api.unsaveJob(jobId);
      showToast('Removed from saved.');
      setMatches(prev => prev.map(m => m.job_id === jobId ? { ...m, is_saved: false } : m));
    } catch {
      showToast('Could not unsave.');
    }
  };

  const handleOpenDetails = (job) => {
    const matchObj = matches.find(m => m.job_id === job.id);
    setSelectedJob(job);
    setSelectedMatchData(matchObj);
    setIsModalOpen(true);
  };

  const tabs = [
    { id: 'all', label: 'All Ranked' },
    { id: 'excellent', label: 'Excellent (90%+)' },
    { id: 'strong', label: 'Strong (80-89%)' },
    { id: 'good', label: 'Good (70-79%)' }
  ];

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8 space-y-8">
      
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 bg-navy-900 text-white px-5 py-3 rounded-2xl shadow-xl text-sm flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Target className="w-6 h-6 text-brand-600" />
            <h1 className="text-3xl font-extrabold text-navy-900">Personalized Match Feed</h1>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Algorithmic recommendations scored and ranked against your candidate profile
          </p>
        </div>

        {/* Sort selector */}
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-slate-500">Sort by:</span>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-3 py-2 text-xs font-semibold rounded-xl border border-slate-200 bg-white text-slate-700"
          >
            <option value="score_desc">Highest Compatibility Score</option>
            <option value="newest">Recently Discovered</option>
          </select>
        </div>
      </div>

      {/* Tier Filter Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-200 pb-3 overflow-x-auto">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTier(tab.id)}
            className={`px-4 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition-colors ${
              activeTier === tab.id
                ? 'bg-brand-600 text-white shadow-xs'
                : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Matches Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((n) => (
            <div key={n} className="bg-white rounded-2xl border border-slate-200 p-6 h-64 animate-pulse" />
          ))}
        </div>
      ) : matches.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {matches.map((m) => (
            <JobCard
              key={m.id}
              job={m.job}
              matchScore={m.score}
              matchTier={m.match_tier}
              strongMatches={m.strong_matches}
              missingSkills={m.missing_skills}
              whyMatched={m.why_matched}
              isSaved={m.is_saved}
              onSave={handleSave}
              onUnsave={handleUnsave}
              onViewDetails={handleOpenDetails}
            />
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-3xl border border-slate-200 p-12 text-center space-y-3">
          <FolderOpen className="w-10 h-10 text-slate-300 mx-auto" />
          <h4 className="font-bold text-navy-900 text-base">No Matches in this Tier</h4>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            Try switching to 'All Ranked' or adjust your minimum score threshold in Profile settings.
          </p>
        </div>
      )}

      {/* Modal */}
      <MatchBreakdownModal
        isOpen={isModalOpen}
        job={selectedJob}
        matchData={selectedMatchData}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSave}
        onUnsave={handleUnsave}
        isSaved={selectedMatchData?.is_saved}
      />

    </div>
  );
}
