import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { 
  ShieldCheck, 
  Database, 
  Play, 
  Loader2, 
  CheckCircle2, 
  AlertTriangle, 
  Layers, 
  Cpu, 
  RefreshCw,
  Globe2
} from 'lucide-react';

export default function AdminPage() {
  const [stats, setStats] = useState(null);
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [syncingSource, setSyncingSource] = useState(null);
  const [toastMessage, setToastMessage] = useState(null);

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  const loadAdminData = async () => {
    setLoading(true);
    try {
      const [st, src] = await Promise.all([
        api.getAdminStats(),
        api.getAdminSources()
      ]);
      setStats(st);
      setSources(src || []);
    } catch (err) {
      console.error('Error loading admin data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAdminData();
  }, []);

  const handleToggleSource = async (adapterKey, currentEnabled) => {
    try {
      await api.updateAdminSource(adapterKey, { enabled: !currentEnabled });
      setSources(prev => prev.map(s => s.adapter_key === adapterKey ? { ...s, enabled: !currentEnabled } : s));
      showToast(`Source adapter ${adapterKey} ${!currentEnabled ? 'enabled' : 'disabled'}.`);
    } catch {
      showToast('Error toggling source.');
    }
  };

  const handleTriggerSync = async (adapterKey) => {
    setSyncingSource(adapterKey);
    try {
      const res = await api.triggerSourceSync(adapterKey);
      showToast(res.message || 'Ingestion completed.');
      await loadAdminData();
    } catch (err) {
      showToast(`Ingestion failed: ${err.message}`);
    } finally {
      setSyncingSource(null);
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

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-6 h-6 text-purple-600" />
            <h1 className="text-3xl font-extrabold text-navy-900">Admin Operations Console</h1>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            System health, permitted source adapters, multi-agent runs, and telemetry
          </p>
        </div>
        <button
          onClick={loadAdminData}
          className="px-4 py-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-xs font-bold text-slate-700 flex items-center gap-1.5"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Metrics</span>
        </button>
      </div>

      {/* High-Level Metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3">
        <div className="bg-white rounded-2xl border border-slate-200 p-4 shadow-xs">
          <span className="text-[10px] font-bold uppercase text-slate-400">Total Users</span>
          <span className="text-2xl font-black text-navy-900 block mt-1">{stats?.total_users || 0}</span>
          <span className="text-[10px] text-slate-400">Candidates: {stats?.total_candidates || 0}</span>
        </div>

        <div className="bg-white rounded-2xl border border-slate-200 p-4 shadow-xs">
          <span className="text-[10px] font-bold uppercase text-brand-500">Active Jobs</span>
          <span className="text-2xl font-black text-brand-700 block mt-1">{stats?.active_jobs || 0}</span>
          <span className="text-[10px] text-slate-400">Total indexed: {stats?.total_jobs || 0}</span>
        </div>

        <div className="bg-white rounded-2xl border border-slate-200 p-4 shadow-xs">
          <span className="text-[10px] font-bold uppercase text-emerald-500">Jobs Today</span>
          <span className="text-2xl font-black text-emerald-700 block mt-1">{stats?.jobs_today || 0}</span>
          <span className="text-[10px] text-emerald-600">Last 24 hours</span>
        </div>

        <div className="bg-white rounded-2xl border border-slate-200 p-4 shadow-xs">
          <span className="text-[10px] font-bold uppercase text-amber-500">Duplicate Rate</span>
          <span className="text-2xl font-black text-amber-700 block mt-1">{stats?.duplicate_rate_percent || 0}%</span>
          <span className="text-[10px] text-slate-400">{stats?.duplicate_count_total || 0} duplicates filtered</span>
        </div>

        <div className="bg-white rounded-2xl border border-slate-200 p-4 shadow-xs">
          <span className="text-[10px] font-bold uppercase text-purple-500">Pipeline Runs</span>
          <span className="text-2xl font-black text-purple-700 block mt-1">{stats?.pipeline_runs_count || 0}</span>
          <span className="text-[10px] text-slate-400">{stats?.failed_runs_count || 0} failed</span>
        </div>

        <div className="bg-white rounded-2xl border border-slate-200 p-4 shadow-xs">
          <span className="text-[10px] font-bold uppercase text-cyan-500">Avg Match Score</span>
          <span className="text-2xl font-black text-cyan-700 block mt-1">{stats?.average_match_score || 0}%</span>
          <span className="text-[10px] text-slate-400">Algorithmic quality</span>
        </div>
      </div>

      {/* Source Adapter Manager */}
      <div className="bg-white rounded-3xl border border-slate-200 p-6 shadow-xs space-y-4">
        <div>
          <h3 className="font-bold text-navy-900 text-lg flex items-center gap-2">
            <Globe2 className="w-5 h-5 text-brand-600" />
            Permitted Job Source Adapters
          </h3>
          <p className="text-xs text-slate-500">
            Compliant, public API source connectors. No anti-bot bypass or unauthorized scraping is permitted.
          </p>
        </div>

        <div className="divide-y divide-slate-100">
          {sources.map((src) => (
            <div key={src.id} className="py-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <h4 className="font-extrabold text-navy-900 text-sm">{src.name}</h4>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md border ${
                    src.enabled ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-slate-100 text-slate-500 border-slate-200'
                  }`}>
                    {src.enabled ? 'ACTIVE' : 'DISABLED'}
                  </span>
                  <span className="text-[11px] font-mono text-slate-400 bg-slate-50 px-1.5 py-0.5 rounded">
                    {src.adapter_key}
                  </span>
                </div>
                <p className="text-xs text-slate-500">{src.description}</p>
                <div className="text-[11px] text-slate-400 flex items-center gap-3 pt-1">
                  <span>Endpoint: <code className="text-slate-600 font-mono">{src.base_url}</code></span>
                  <span>Total Fetched: <strong className="text-slate-700">{src.jobs_fetched_total}</strong></span>
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-2 shrink-0">
                <button
                  onClick={() => handleToggleSource(src.adapter_key, src.enabled)}
                  className={`px-3 py-1.5 rounded-xl text-xs font-semibold border transition-colors ${
                    src.enabled 
                      ? 'border-red-200 text-red-600 hover:bg-red-50' 
                      : 'border-emerald-200 text-emerald-700 hover:bg-emerald-50'
                  }`}
                >
                  {src.enabled ? 'Disable' : 'Enable'}
                </button>

                <button
                  onClick={() => handleTriggerSync(src.adapter_key)}
                  disabled={syncingSource === src.adapter_key}
                  className="px-4 py-1.5 bg-brand-600 hover:bg-brand-700 text-white font-semibold text-xs rounded-xl shadow-xs flex items-center gap-1.5 disabled:opacity-50"
                >
                  {syncingSource === src.adapter_key ? (
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  ) : (
                    <Play className="w-3.5 h-3.5 fill-white" />
                  )}
                  <span>Run Ingestion</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Distribution by Domain */}
      <div className="bg-white rounded-3xl border border-slate-200 p-6 shadow-xs space-y-4">
        <h3 className="font-bold text-navy-900 text-lg flex items-center gap-2">
          <Layers className="w-5 h-5 text-indigo-600" />
          Job Distribution by Career Domain
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {stats?.jobs_by_domain?.map((d, i) => (
            <div key={i} className="bg-slate-50 p-3.5 rounded-2xl border border-slate-100 flex items-center justify-between">
              <span className="text-xs font-bold text-navy-900 truncate pr-2">{d.domain}</span>
              <span className="text-xs font-black text-brand-600 bg-white px-2 py-0.5 rounded-md border border-slate-200">
                {d.count}
              </span>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
}
