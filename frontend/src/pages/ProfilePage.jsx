import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import { 
  User, 
  Upload, 
  RefreshCw, 
  CheckCircle2, 
  Sliders, 
  Sparkles, 
  Plus, 
  X,
  GraduationCap,
  Briefcase
} from 'lucide-react';

export default function ProfilePage({ setActivePage }) {
  const { currentUser, refreshUser } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [newSkill, setNewSkill] = useState('');
  const [toastMessage, setToastMessage] = useState(null);
  const [reanalyzing, setReanalyzing] = useState(false);

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  const loadProfile = async () => {
    setLoading(true);
    try {
      const p = await api.getProfile();
      setProfile(p);
    } catch (err) {
      console.error('Error loading profile:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProfile();
  }, []);

  const handleAddSkill = async (e) => {
    e.preventDefault();
    if (!newSkill.trim() || !profile) return;
    const updatedSkills = [...(profile.skills || []), newSkill.trim()];
    try {
      const updated = await api.updateProfile({ skills: updatedSkills });
      setProfile(updated);
      setNewSkill('');
      showToast('Skill added.');
      await refreshUser();
    } catch {
      showToast('Error adding skill.');
    }
  };

  const handleRemoveSkill = async (skillToRemove) => {
    if (!profile) return;
    const updatedSkills = profile.skills.filter(s => s !== skillToRemove);
    try {
      const updated = await api.updateProfile({ skills: updatedSkills });
      setProfile(updated);
      showToast('Skill removed.');
      await refreshUser();
    } catch {
      showToast('Error removing skill.');
    }
  };

  const handleUpdatePreferences = async (field, value) => {
    try {
      const updated = await api.updateProfile({ [field]: value });
      setProfile(updated);
      showToast('Preferences updated.');
      await refreshUser();
    } catch {
      showToast('Failed to update preference.');
    }
  };

  const handleReanalyze = async () => {
    setReanalyzing(true);
    try {
      const res = await api.reanalyzeProfile();
      showToast(res.message || 'Profile re-analyzed.');
      await loadProfile();
      await refreshUser();
    } catch (err) {
      showToast('Re-analysis failed.');
    } finally {
      setReanalyzing(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 space-y-8">
      
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
            <User className="w-6 h-6 text-brand-600" />
            <h1 className="text-3xl font-extrabold text-navy-900">Candidate Career Profile</h1>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Maintained by Profile Agent to optimize your personalized matching accuracy
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleReanalyze}
            disabled={reanalyzing}
            className="px-4 py-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-xs font-bold text-slate-700 flex items-center gap-1.5 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${reanalyzing ? 'animate-spin' : ''}`} />
            <span>Re-analyze</span>
          </button>
          <button
            onClick={() => setActivePage('onboarding')}
            className="px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold rounded-xl flex items-center gap-1.5"
          >
            <Upload className="w-3.5 h-3.5" />
            <span>Replace Resume</span>
          </button>
        </div>
      </div>

      {loading ? (
        <div className="h-64 bg-white rounded-3xl border border-slate-200 p-8 animate-pulse" />
      ) : profile ? (
        <div className="space-y-6">
          
          {/* Completeness & Personal Info */}
          <div className="bg-white rounded-3xl border border-slate-200 p-6 sm:p-8 shadow-xs space-y-6">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <div>
                <h3 className="text-2xl font-bold text-navy-900">{profile.name || currentUser?.name}</h3>
                <p className="text-xs text-slate-500 mt-0.5">{profile.email || currentUser?.email}</p>
              </div>
              <div className="text-right">
                <span className="text-xs font-bold text-emerald-800 bg-emerald-50 px-3.5 py-1 rounded-full border border-emerald-200">
                  Profile Strength: {profile.completeness_score}%
                </span>
              </div>
            </div>

            {/* Education & Experience Details */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="bg-slate-50 p-4 rounded-2xl border border-slate-100 space-y-1">
                <span className="text-xs font-bold text-slate-500 uppercase flex items-center gap-1">
                  <GraduationCap className="w-4 h-4 text-brand-600" /> Education
                </span>
                <p className="text-sm font-bold text-navy-900">
                  {profile.education?.[0]?.degree || 'B.Tech'} in {profile.education?.[0]?.field || 'AI & Data Science'}
                </p>
                <p className="text-xs text-slate-500">Graduation Year: {profile.education?.[0]?.graduation_year || 2027}</p>
              </div>

              <div className="bg-slate-50 p-4 rounded-2xl border border-slate-100 space-y-1">
                <span className="text-xs font-bold text-slate-500 uppercase flex items-center gap-1">
                  <Briefcase className="w-4 h-4 text-indigo-600" /> Career Stage
                </span>
                <p className="text-sm font-bold text-navy-900 capitalize">
                  {profile.experience_level} ({profile.years_of_experience || 0} years experience)
                </p>
                <p className="text-xs text-slate-500">Targeting internships and entry-level positions</p>
              </div>
            </div>

            {/* Technical Skills with Add / Remove */}
            <div className="space-y-3">
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
                Technical Skills ({profile.skills?.length || 0})
              </label>
              <div className="flex flex-wrap gap-2">
                {profile.skills?.map((sk, idx) => (
                  <span key={idx} className="bg-slate-100 text-slate-800 text-xs font-semibold px-3 py-1.5 rounded-xl border border-slate-200 flex items-center gap-1.5">
                    {sk}
                    <button 
                      onClick={() => handleRemoveSkill(sk)}
                      className="text-slate-400 hover:text-red-500"
                    >
                      <X className="w-3.5 h-3.5" />
                    </button>
                  </span>
                ))}
              </div>

              {/* Add Skill Input */}
              <form onSubmit={handleAddSkill} className="flex gap-2 max-w-sm pt-2">
                <input
                  type="text"
                  value={newSkill}
                  onChange={(e) => setNewSkill(e.target.value)}
                  placeholder="Add skill (e.g. PyTorch, Docker)..."
                  className="px-3 py-2 text-xs rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-brand-500/20 flex-1"
                />
                <button
                  type="submit"
                  className="px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold rounded-xl"
                >
                  <Plus className="w-4 h-4" />
                </button>
              </form>
            </div>

            {/* Target Domains & Recommended Roles */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2 border-t border-slate-100">
              <div>
                <span className="text-xs font-bold text-slate-700 uppercase tracking-wider block mb-2">Target Domains</span>
                <div className="flex flex-wrap gap-1.5">
                  {profile.domains?.map((d, i) => (
                    <span key={i} className="text-xs font-bold bg-brand-50 text-brand-700 border border-brand-200 px-3 py-1 rounded-lg">
                      {d}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <span className="text-xs font-bold text-slate-700 uppercase tracking-wider block mb-2">Recommended Roles</span>
                <div className="flex flex-wrap gap-1.5">
                  {profile.recommended_roles?.map((r, i) => (
                    <span key={i} className="text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200 px-3 py-1 rounded-lg">
                      {r}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Recommendation Preferences */}
          <div className="bg-white rounded-3xl border border-slate-200 p-6 sm:p-8 shadow-xs space-y-4">
            <h4 className="font-bold text-navy-900 text-base flex items-center gap-2">
              <Sliders className="w-4 h-4 text-brand-600" />
              Recommendation Calibration
            </h4>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Location Preference
                </label>
                <select
                  value={profile.remote_preference || 'any'}
                  onChange={(e) => handleUpdatePreferences('remote_preference', e.target.value)}
                  className="w-full p-2.5 rounded-xl border border-slate-300 text-sm font-medium focus:outline-none"
                >
                  <option value="any">Any (Remote, Hybrid, Onsite)</option>
                  <option value="remote">Remote Preferred</option>
                  <option value="hybrid">Hybrid</option>
                  <option value="onsite">Onsite Only</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Minimum Score Threshold ({profile.minimum_match_score || 60}%)
                </label>
                <input
                  type="range"
                  min="30"
                  max="90"
                  step="5"
                  value={profile.minimum_match_score || 60}
                  onChange={(e) => handleUpdatePreferences('minimum_match_score', Number(e.target.value))}
                  className="w-full accent-brand-600 cursor-pointer mt-2"
                />
              </div>
            </div>
          </div>

        </div>
      ) : (
        <div className="bg-white rounded-3xl border border-slate-200 p-12 text-center space-y-4">
          <p className="text-slate-500 text-sm">No candidate profile found.</p>
          <button
            onClick={() => setActivePage('onboarding')}
            className="px-6 py-2.5 bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold rounded-xl"
          >
            Upload Resume
          </button>
        </div>
      )}

    </div>
  );
}
