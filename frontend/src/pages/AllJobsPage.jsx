import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import JobCard from '../components/JobCard';
import MatchBreakdownModal from '../components/MatchBreakdownModal';
import { 
  Search, 
  Filter, 
  ChevronLeft, 
  ChevronRight, 
  Briefcase, 
  Building2, 
  MapPin, 
  Clock, 
  CheckCircle2 
} from 'lucide-react';

export default function AllJobsPage() {
  const [jobs, setJobs] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);

  // Filters
  const [query, setQuery] = useState('');
  const [domain, setDomain] = useState('all');
  const [empType, setEmpType] = useState('all');
  const [expLevel, setExpLevel] = useState('all');
  const [locType, setLocType] = useState('all');

  // Modal
  const [selectedJob, setSelectedJob] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState(null);

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  const fetchJobs = async (pageNumber = 1) => {
    setLoading(true);
    try {
      const res = await api.getJobs({
        q: query,
        domain: domain,
        employment_type: empType,
        experience_level: expLevel,
        location_type: locType,
        page: pageNumber,
        page_size: 12
      });
      setJobs(res.items || []);
      setTotal(res.total || 0);
      setPage(res.page || 1);
      setTotalPages(res.total_pages || 1);
    } catch (err) {
      console.error('Error fetching jobs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs(1);
  }, [domain, empType, expLevel, locType]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchJobs(1);
  };

  const handleSave = async (jobId) => {
    try {
      await api.saveJob(jobId);
      showToast('Saved to your collection.');
    } catch {
      showToast('Could not save job.');
    }
  };

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8 space-y-8">
      
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 bg-navy-900 text-white px-5 py-3 rounded-2xl shadow-xl text-sm flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Page Header */}
      <div>
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-brand-600" />
          <h1 className="text-3xl font-extrabold text-navy-900">Explore Opportunities</h1>
        </div>
        <p className="text-xs text-slate-500 mt-1">
          Showing {total} active job and internship postings discovered from compliant sources
        </p>
      </div>

      {/* Search & Filter Toolbar */}
      <div className="bg-white rounded-2xl border border-slate-200 p-4 shadow-xs space-y-3">
        <form onSubmit={handleSearchSubmit} className="flex gap-2">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search by title, technology, or company name..."
              className="w-full pl-10 pr-4 py-2.5 text-sm rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
            />
          </div>
          <button
            type="submit"
            className="px-5 py-2.5 bg-brand-600 hover:bg-brand-700 text-white font-semibold text-xs rounded-xl shadow-xs"
          >
            Search
          </button>
        </form>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-slate-100">
          <select
            value={domain}
            onChange={(e) => setDomain(e.target.value)}
            className="px-3 py-2 text-xs font-medium rounded-xl border border-slate-200 bg-slate-50 text-slate-700"
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

          <select
            value={empType}
            onChange={(e) => setEmpType(e.target.value)}
            className="px-3 py-2 text-xs font-medium rounded-xl border border-slate-200 bg-slate-50 text-slate-700"
          >
            <option value="all">All Types</option>
            <option value="full_time">Full Time</option>
            <option value="internship">Internship</option>
            <option value="contract">Contract</option>
          </select>

          <select
            value={expLevel}
            onChange={(e) => setExpLevel(e.target.value)}
            className="px-3 py-2 text-xs font-medium rounded-xl border border-slate-200 bg-slate-50 text-slate-700"
          >
            <option value="all">All Experience</option>
            <option value="fresher">Fresher (0-1 yrs)</option>
            <option value="entry_level">Entry Level</option>
            <option value="junior">Junior</option>
            <option value="mid_level">Mid Level</option>
            <option value="senior">Senior</option>
          </select>

          <select
            value={locType}
            onChange={(e) => setLocType(e.target.value)}
            className="px-3 py-2 text-xs font-medium rounded-xl border border-slate-200 bg-slate-50 text-slate-700"
          >
            <option value="all">All Locations</option>
            <option value="remote">Remote Only</option>
            <option value="hybrid">Hybrid</option>
            <option value="onsite">Onsite</option>
          </select>
        </div>
      </div>

      {/* Jobs Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((n) => (
            <div key={n} className="bg-white rounded-2xl border border-slate-200 p-6 h-60 animate-pulse" />
          ))}
        </div>
      ) : jobs.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {jobs.map((job) => (
            <JobCard
              key={job.id}
              job={job}
              onSave={handleSave}
              onViewDetails={(j) => { setSelectedJob(j); setIsModalOpen(true); }}
            />
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-3xl border border-slate-200 p-12 text-center">
          <p className="text-slate-500 text-sm">No opportunities match the selected criteria.</p>
        </div>
      )}

      {/* Pagination Controls */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-3 pt-6">
          <button
            onClick={() => fetchJobs(page - 1)}
            disabled={page <= 1}
            className="p-2.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 disabled:opacity-40 text-slate-700"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <span className="text-xs font-bold text-slate-700">
            Page {page} of {totalPages}
          </span>
          <button
            onClick={() => fetchJobs(page + 1)}
            disabled={page >= totalPages}
            className="p-2.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 disabled:opacity-40 text-slate-700"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      )}

      <MatchBreakdownModal
        isOpen={isModalOpen}
        job={selectedJob}
        matchData={{ score: 75, match_tier: 'Good Match', breakdown: {} }}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSave}
      />

    </div>
  );
}
