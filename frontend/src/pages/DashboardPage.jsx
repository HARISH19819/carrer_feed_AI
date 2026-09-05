import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import AgentCard from '../components/AgentCard';
import PipelineVisualizer from '../components/PipelineVisualizer';
import JobCard from '../components/JobCard';
import MatchBreakdownModal from '../components/MatchBreakdownModal';
import { 
  Sparkles, 
  Search, 
  SlidersHorizontal, 
  RefreshCw, 
  CheckCircle2, 
  AlertCircle, 
  Layers, 
  Target,
  ArrowRight,
  TrendingUp,
  FolderOpen
} from 'lucide-react';

export default function DashboardPage({ setActivePage }) {
  const { currentUser, refreshUser } = useAuth();
  
  // State
  const [profile, setProfile] = useState(null);
  const [matches, setMatches] = useState([]);
  const [loadingMatches, setLoadingMatches] = useState(true);
  const [pipelineData, setPipelineData] = useState(null);
  const [runningAgent, setRunningAgent] = useState(null);
  const [runningPipeline, setRunningPipeline] = useState(false);
  
  // Search & Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDomain, setSelectedDomain] = useState('all');
  const [selectedTier, setSelectedTier] = useState('all');

  // Modal State
  const [selectedJob, setSelectedJob] = useState(null);
  const [selectedMatchData, setSelectedMatchData] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Toast / Status Message
  const [toastMessage, setToastMessage] = useState(null);

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 4000);
  };

  const loadData = async () => {
    try {
      // 1. Fetch profile
      try {
        const p = await api.getProfile();
        setProfile(p);
      } catch {
        setProfile(null);
      }

      // 2. Fetch matches
      const matchRes = await api.getMatches({ page_size: 20 });
      setMatches(matchRes.items || []);

      // 3. Fetch pipeline status
      const pipeRes = await api.getPipelineStatus();
      setPipelineData(pipeRes);
    } catch (err) {
      console.error('Error loading dashboard data:', err);
    } finally {
      setLoadingMatches(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleRunAgent = async (agentId) => {
    setRunningAgent(agentId);
    try {
      if (agentId === 'profile') {
        setActivePage('profile');
        return;
      }
      await api.runPipeline(agentId);
      showToast(`Agent executed successfully.`);
      await loadData();
    } catch (err) {
      showToast(`Agent run error: ${err.message}`);
    } finally {
      setRunningAgent(null);
    }
  };

  const handleRunFullPipeline = async () => {
    setRunningPipeline(true);
    try {
      const res = await api.runPipeline('all');
      showToast(`Full Multi-Agent Pipeline completed! Recommendations refreshed.`);
      await loadData();
      await refreshUser();
    } catch (err) {
      showToast(`Pipeline execution failed: ${err.message}`);
    } finally {
      setRunningPipeline(false);
    }
  };

  const handleSaveJob = async (jobId) => {
    try {
      await api.saveJob(jobId);
      showToast('Job saved to your list.');
      setMatches(prev => prev.map(m => m.job_id === jobId ? { ...m, is_saved: true } : m));
    } catch (err) {
      showToast('Failed to save job.');
    }
  };

  const handleUnsaveJob = async (jobId) => {
    try {
      await api.unsaveJob(jobId);
      showToast('Job removed from saved.');
      setMatches(prev => prev.map(m => m.job_id === jobId ? { ...m, is_saved: false } : m));
    } catch (err) {
      showToast('Failed to unsave job.');
    }
  };

  const handleApplyClick = (jobId) => {
    // Direct source apply
  };

  const handleOpenDetails = (job) => {
    const matchObj = matches.find(m => m.job_id === job.id);
    setSelectedJob(job);
    setSelectedMatchData(matchObj || { score: 75, match_tier: 'Good Match', breakdown: {} });
    setIsModalOpen(true);
  };

  // Filtered matches
  const filteredMatches = matches.filter(m => {
    const job = m.job;
    if (!job) return false;
    
    // Search query
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const titleMatch = job.title?.toLowerCase().includes(q);
      const companyMatch = job.company?.toLowerCase().includes(q);
      const skillsMatch = job.skills?.some(s => s.toLowerCase().includes(q));
      if (!titleMatch && !companyMatch && !skillsMatch) return false;
    }

    // Domain filter
    if (selectedDomain !== 'all' && job.domain !== selectedDomain) {
      return false;
    }

    // Tier filter
    if (selectedTier !== 'all') {
      if (selectedTier === 'excellent' && m.score < 90) return false;
      if (selectedTier === 'strong' && (m.score < 80 || m.score >= 90)) return false;
      if (selectedTier === 'good' && (m.score < 70 || m.score >= 80)) return false;
    }

    return true;
  });

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8 space-y-8">
      
      {/* Toast alert */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 bg-navy-900 text-white px-5 py-3 rounded-2xl shadow-xl border border-slate-700 text-sm font-medium flex items-center gap-2 animate-slideUp">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* TOP PROFILE READINESS CARD */}
      {profile ? (
        <div className="bg-white rounded-3xl border border-slate-200 p-6 sm:p-8 shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <div className="flex items-center gap-2">
              <span className="bg-emerald-50 text-emerald-800 text-xs font-bold px-3 py-1 rounded-full border border-emerald-200 flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                PROFILE READY
              </span>
              <span className="text-xs text-slate-400 font-medium">Domain:</span>
              <span className="text-xs font-bold text-navy-900 bg-slate-100 px-2.5 py-0.5 rounded-lg">
                {profile.domains?.[0] || 'Machine Learning'}
              </span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-navy-900 tracking-tight">
              Welcome back, {profile.name || currentUser?.name}!
            </h2>
            <div className="flex flex-wrap items-center gap-1.5 pt-1">
              <span className="text-xs text-slate-500 font-semibold mr-1">Skills:</span>
              {profile.skills?.slice(0, 6).map((sk, idx) => (
                <span key={idx} className="bg-slate-100 text-slate-800 text-xs font-medium px-2.5 py-0.5 rounded-md border border-slate-200">
                  {sk}
                </span>
              ))}
              {(profile.skills?.length || 0) > 6 && (
                <span className="text-xs text-slate-400 font-medium">+{profile.skills.length - 6} more</span>
              )}
            </div>
          </div>

          <div className="flex items-center gap-4 shrink-0">
            <div className="text-center bg-slate-50 p-4 rounded-2xl border border-slate-100 min-w-[120px]">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Strength</span>
              <span className="text-2xl font-black text-brand-600 block mt-0.5">{profile.completeness_score || 85}%</span>
              <span className="text-[10px] text-emerald-600 font-semibold">Ready to Match</span>
            </div>
            <button
              onClick={() => setActivePage('profile')}
              className="px-5 py-3 rounded-xl border border-slate-200 hover:border-slate-300 bg-white hover:bg-slate-50 text-slate-700 text-xs font-bold transition-colors shadow-2xs"
            >
              Edit Profile
            </button>
          </div>
        </div>
      ) : (
        <div className="bg-brand-50 border border-brand-200 rounded-3xl p-6 flex items-center justify-between gap-4">
          <div>
            <h3 className="font-bold text-brand-900 text-lg">No Resume Uploaded Yet</h3>
            <p className="text-xs text-brand-700 mt-1">
              Upload your resume so our AI agents can build your profile and personalize recommendations.
            </p>
          </div>
          <button
            onClick={() => setActivePage('onboarding')}
            className="px-6 py-2.5 bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold rounded-xl shrink-0"
          >
            Upload Resume
          </button>
        </div>
      )}

      {/* 4 AGENT CARDS */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-extrabold text-navy-900 text-lg">Active AI Agents</h3>
            <p className="text-xs text-slate-500">Autonomous workers operating on your job discovery stream</p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {pipelineData?.agent_cards?.map((card) => (
            <AgentCard
              key={card.agent_id}
              card={card}
              onRun={handleRunAgent}
              isRunning={runningAgent === card.agent_id}
            />
          )) || (
            <div className="col-span-4 text-center py-6 text-xs text-slate-400">Loading agent telemetry...</div>
          )}
        </div>
      </div>

      {/* FULL PIPELINE STREAM VISUALIZER */}
      <PipelineVisualizer
        onRunFullPipeline={handleRunFullPipeline}
        isRunning={runningPipeline}
        lastRun={pipelineData?.recent_runs?.[0]}
      />

      {/* TOP MATCHES SECTION */}
      <div className="space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-brand-600" />
              <h2 className="text-2xl font-extrabold text-navy-900">Your Top Recommended Matches</h2>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Ranked descending by compatibility score with transparent explainability
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setActivePage('matches')}
              className="text-xs font-bold text-brand-600 hover:text-brand-700 flex items-center gap-1"
            >
              <span>View All Matches</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Search & Filter Toolbar */}
        <div className="bg-white rounded-2xl border border-slate-200 p-4 shadow-xs flex flex-col sm:flex-row items-center gap-3">
          <div className="relative flex-1 w-full">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search title, company, skill (e.g. Python, Machine Learning)..."
              className="w-full pl-10 pr-4 py-2 text-sm rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
            />
          </div>

          {/* Domain Filter */}
          <select
            value={selectedDomain}
            onChange={(e) => setSelectedDomain(e.target.value)}
            className="w-full sm:w-auto px-3 py-2 text-xs font-semibold rounded-xl border border-slate-200 bg-slate-50 text-slate-700 focus:outline-none"
          >
            <option value="all">All Domains</option>
            <option value="Machine Learning">Machine Learning</option>
            <option value="Artificial Intelligence">Artificial Intelligence</option>
            <option value="Data Science">Data Science</option>
            <option value="Software Development">Software Development</option>
            <option value="Backend Development">Backend Development</option>
            <option value="Frontend Development">Frontend Development</option>
            <option value="DevOps">DevOps & Cloud</option>
          </select>

          {/* Tier Filter */}
          <select
            value={selectedTier}
            onChange={(e) => setSelectedTier(e.target.value)}
            className="w-full sm:w-auto px-3 py-2 text-xs font-semibold rounded-xl border border-slate-200 bg-slate-50 text-slate-700 focus:outline-none"
          >
            <option value="all">All Match Tiers</option>
            <option value="excellent">Excellent Match (90%+)</option>
            <option value="strong">Strong Match (80-89%)</option>
            <option value="good">Good Match (70-79%)</option>
          </select>
        </div>

        {/* Jobs Grid */}
        {loadingMatches ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((n) => (
              <div key={n} className="bg-white rounded-2xl border border-slate-200 p-6 h-64 animate-pulse space-y-4">
                <div className="h-4 bg-slate-200 rounded w-1/3" />
                <div className="h-6 bg-slate-200 rounded w-3/4" />
                <div className="h-4 bg-slate-200 rounded w-1/2" />
                <div className="h-16 bg-slate-100 rounded" />
              </div>
            ))}
          </div>
        ) : filteredMatches.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredMatches.map((m) => (
              <JobCard
                key={m.id}
                job={m.job}
                matchScore={m.score}
                matchTier={m.match_tier}
                strongMatches={m.strong_matches}
                missingSkills={m.missing_skills}
                whyMatched={m.why_matched}
                isSaved={m.is_saved}
                onSave={handleSaveJob}
                onUnsave={handleUnsaveJob}
                onApplyClick={handleApplyClick}
                onViewDetails={handleOpenDetails}
              />
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-3xl border border-slate-200 p-12 text-center space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-slate-100 flex items-center justify-center text-slate-400 mx-auto">
              <FolderOpen className="w-6 h-6" />
            </div>
            <div>
              <h4 className="font-bold text-navy-900 text-base">No Matching Opportunities Found</h4>
              <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
                Try adjusting your search query, clearing domain filters, or running the Match Agent.
              </p>
            </div>
            <button
              onClick={() => { setSearchQuery(''); setSelectedDomain('all'); setSelectedTier('all'); }}
              className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold"
            >
              Reset Filters
            </button>
          </div>
        )}
      </div>

      {/* Match Breakdown Modal */}
      <MatchBreakdownModal
        isOpen={isModalOpen}
        job={selectedJob}
        matchData={selectedMatchData}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSaveJob}
        onUnsave={handleUnsaveJob}
        onApplyClick={handleApplyClick}
        isSaved={selectedMatchData?.is_saved}
      />

    </div>
  );
}
