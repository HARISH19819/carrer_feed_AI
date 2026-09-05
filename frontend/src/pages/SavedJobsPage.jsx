import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Bookmark, Building2, MapPin, Trash2, ExternalLink, Info, CheckCircle2, FolderOpen } from 'lucide-react';
import MatchBreakdownModal from '../components/MatchBreakdownModal';

export default function SavedJobsPage() {
  const [savedItems, setSavedItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedJob, setSelectedJob] = useState(null);
  const [selectedMatchData, setSelectedMatchData] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState(null);

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  const fetchSaved = async () => {
    setLoading(true);
    try {
      const res = await api.getSavedJobs();
      setSavedItems(res.items || []);
    } catch (err) {
      console.error('Error loading saved jobs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSaved();
  }, []);

  const handleRemove = async (jobId) => {
    try {
      await api.unsaveJob(jobId);
      setSavedItems(prev => prev.filter(item => item.job_id !== jobId));
      showToast('Removed from saved list.');
    } catch {
      showToast('Could not remove job.');
    }
  };

  const handleOpenDetails = (job, score, tier) => {
    setSelectedJob(job);
    setSelectedMatchData({ score: score || 75, match_tier: tier || 'Good Match', breakdown: {}, is_saved: true });
    setIsModalOpen(true);
  };

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8 space-y-8">
      
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 bg-navy-900 text-white px-5 py-3 rounded-2xl shadow-xl text-sm flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Header */}
      <div>
        <div className="flex items-center gap-2">
          <Bookmark className="w-6 h-6 text-amber-500 fill-amber-500" />
          <h1 className="text-3xl font-extrabold text-navy-900">Saved Opportunities</h1>
        </div>
        <p className="text-xs text-slate-500 mt-1">
          {savedItems.length} opportunities bookmarked for review and applications
        </p>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((n) => (
            <div key={n} className="bg-white rounded-2xl border border-slate-200 p-6 h-48 animate-pulse" />
          ))}
        </div>
      ) : savedItems.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {savedItems.map((item) => {
            const job = item.job;
            if (!job) return null;
            return (
              <div key={item.id} className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs flex flex-col justify-between space-y-4">
                <div>
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <span className="text-xs font-semibold text-brand-700 bg-brand-50 px-2 py-0.5 rounded">
                      {job.domain}
                    </span>
                    {item.score && (
                      <span className="text-xs font-extrabold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
                        {item.score}% Match
                      </span>
                    )}
                  </div>
                  <h3 className="font-bold text-navy-900 text-base line-clamp-1">{job.title}</h3>
                  <div className="flex items-center gap-3 text-xs text-slate-500 mt-1">
                    <span className="flex items-center gap-1 font-medium text-slate-700">
                      <Building2 className="w-3.5 h-3.5 text-slate-400" />
                      {job.company}
                    </span>
                    <span className="flex items-center gap-1">
                      <MapPin className="w-3.5 h-3.5 text-slate-400" />
                      {job.location}
                    </span>
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleRemove(item.job_id)}
                      className="p-2 rounded-lg border border-red-200 text-red-600 hover:bg-red-50 text-xs transition-colors"
                      title="Remove from saved"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleOpenDetails(job, item.score, item.match_tier)}
                      className="px-3 py-2 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-semibold"
                    >
                      Details
                    </button>
                  </div>

                  <a
                    href={job.application_url || job.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1.5 px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold rounded-lg shadow-xs"
                  >
                    <span>Apply</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="bg-white rounded-3xl border border-slate-200 p-12 text-center space-y-3">
          <FolderOpen className="w-10 h-10 text-slate-300 mx-auto" />
          <h4 className="font-bold text-navy-900 text-base">No Saved Jobs Yet</h4>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            Bookmark interesting jobs while exploring your recommendations to easily access them here.
          </p>
        </div>
      )}

      <MatchBreakdownModal
        isOpen={isModalOpen}
        job={selectedJob}
        matchData={selectedMatchData}
        onClose={() => setIsModalOpen(false)}
        onUnsave={handleRemove}
        isSaved={true}
      />

    </div>
  );
}
