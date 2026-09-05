import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import { 
  Upload, 
  FileText, 
  CheckCircle2, 
  Sparkles, 
  Loader2, 
  ArrowRight, 
  Edit3, 
  Layers, 
  Target, 
  Sliders,
  Check
} from 'lucide-react';

export default function OnboardingPage({ setActivePage }) {
  const { refreshUser } = useAuth();
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [currentStep, setCurrentStep] = useState(0); // 0 = upload, 1 = processing, 2 = review
  const [parsedProfile, setParsedProfile] = useState(null);
  const [error, setError] = useState(null);

  // Editable preferences
  const [preferredDomains, setPreferredDomains] = useState([]);
  const [preferredRoles, setPreferredRoles] = useState([]);
  const [preferredLocations, setPreferredLocations] = useState(['Remote']);
  const [preferredJobTypes, setPreferredJobTypes] = useState(['internship', 'full_time']);
  const [remotePreference, setRemotePreference] = useState('any');
  const [minMatchScore, setMinMatchScore] = useState(60);

  const processingStages = [
    'Reading resume document format...',
    'Extracting & normalizing technical skills...',
    'Identifying domain taxonomy alignment...',
    'Inferring suitable role titles...',
    'Generating unified career intelligence profile...'
  ];

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleAnalyzeResume = async () => {
    if (!file) return;
    setError(null);
    setUploading(true);
    setCurrentStep(1);

    try {
      const profile = await api.uploadResume(file);
      setParsedProfile(profile);
      setPreferredDomains(profile.domains || []);
      setPreferredRoles(profile.recommended_roles || []);
      setPreferredLocations(profile.preferred_locations || ['Remote']);
      setPreferredJobTypes(profile.preferred_job_types || ['internship', 'full_time']);
      setRemotePreference(profile.remote_preference || 'any');
      setMinMatchScore(profile.minimum_match_score || 60);

      await refreshUser();
      setCurrentStep(2);
    } catch (err) {
      setError(err.message || "We couldn't read this resume. Please ensure it is an uncorrupted PDF or DOCX file.");
      setCurrentStep(0);
    } finally {
      setUploading(false);
    }
  };

  const handleConfirmProfile = async () => {
    try {
      await api.updateProfile({
        domains: preferredDomains,
        recommended_roles: preferredRoles,
        preferred_locations: preferredLocations,
        preferred_job_types: preferredJobTypes,
        remote_preference: remotePreference,
        minimum_match_score: minMatchScore
      });
      await refreshUser();
      setActivePage('dashboard');
    } catch (err) {
      setError('Error updating preferences.');
    }
  };

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6">
      
      {/* Header */}
      <div className="text-center mb-8 space-y-2">
        <span className="text-xs font-bold uppercase tracking-widest text-brand-600 bg-brand-50 px-3 py-1 rounded-full border border-brand-200">
          Career Profile Builder
        </span>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-navy-900">
          {currentStep === 2 ? 'Confirm Your Career Profile' : 'Upload Your Resume'}
        </h1>
        <p className="text-sm text-slate-500 max-w-xl mx-auto">
          {currentStep === 2
            ? 'Our Resume Agent extracted your profile. Review and adjust your preferences.'
            : 'JobFusion AI will automatically extract your skills, education, and domain compatibility.'}
        </p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-2xl text-red-700 text-sm">
          {error}
        </div>
      )}

      {/* STEP 0: Upload Resume Area */}
      {currentStep === 0 && (
        <div className="bg-white rounded-3xl border border-slate-200 p-8 shadow-sm space-y-6">
          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            className="border-2 border-dashed border-slate-300 hover:border-brand-500 bg-slate-50/60 hover:bg-brand-50/20 rounded-2xl p-10 text-center transition-all cursor-pointer flex flex-col items-center justify-center space-y-4"
            onClick={() => document.getElementById('resume-file-input').click()}
          >
            <input
              id="resume-file-input"
              type="file"
              accept=".pdf,.docx,.txt"
              className="hidden"
              onChange={handleFileChange}
            />
            <div className="w-16 h-16 rounded-2xl bg-brand-50 border border-brand-100 flex items-center justify-center text-brand-600 shadow-xs">
              <Upload className="w-8 h-8" />
            </div>
            <div>
              <p className="text-base font-bold text-navy-900">
                {file ? file.name : 'Drop your resume here, or click to browse'}
              </p>
              <p className="text-xs text-slate-500 mt-1">
                Accepted formats: PDF, DOCX, TXT (Max size 10MB)
              </p>
            </div>
            {file && (
              <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 px-3 py-1 rounded-full border border-emerald-200">
                ✓ Ready for analysis ({(file.size / 1024).toFixed(1)} KB)
              </span>
            )}
          </div>

          <div className="flex justify-end">
            <button
              onClick={handleAnalyzeResume}
              disabled={!file || uploading}
              className="px-8 py-3.5 bg-brand-600 hover:bg-brand-700 active:bg-brand-800 text-white font-bold text-sm rounded-xl shadow-md shadow-brand-500/25 flex items-center gap-2 transition-all disabled:opacity-50"
            >
              <Sparkles className="w-4 h-4" />
              <span>Analyze Resume</span>
            </button>
          </div>
        </div>
      )}

      {/* STEP 1: Animated Processing State */}
      {currentStep === 1 && (
        <div className="bg-white rounded-3xl border border-slate-200 p-12 text-center shadow-md space-y-6">
          <div className="w-16 h-16 rounded-2xl bg-brand-50 flex items-center justify-center text-brand-600 mx-auto animate-bounce">
            <Loader2 className="w-8 h-8 animate-spin" />
          </div>
          <div className="space-y-2">
            <h3 className="text-xl font-bold text-navy-900">Analyzing Your Candidate Profile</h3>
            <p className="text-xs text-slate-500">Autonomous Resume Agent is processing your career document...</p>
          </div>
          <div className="max-w-md mx-auto space-y-2 text-left pt-4">
            {processingStages.map((stg, i) => (
              <div key={i} className="flex items-center gap-2 text-xs text-slate-600 bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                <Check className="w-4 h-4 text-emerald-500 shrink-0" />
                <span>{stg}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* STEP 2: Profile Review & Preferences Configuration */}
      {currentStep === 2 && parsedProfile && (
        <div className="space-y-6">
          {/* Extracted Card */}
          <div className="bg-white rounded-3xl border border-slate-200 p-6 shadow-sm space-y-6">
            <div className="flex items-start justify-between border-b border-slate-100 pb-4">
              <div>
                <h3 className="text-xl font-bold text-navy-900">{parsedProfile.name || 'Candidate'}</h3>
                <p className="text-xs text-slate-500">
                  {parsedProfile.email} • {parsedProfile.education?.[0]?.degree || 'B.Tech'} ({parsedProfile.education?.[0]?.field || 'Computer Science'})
                </p>
              </div>
              <div className="text-right">
                <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 px-3 py-1 rounded-full border border-emerald-200">
                  Profile Strength: {parsedProfile.completeness_score}%
                </span>
              </div>
            </div>

            {/* Extracted Skills */}
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Extracted Skills ({parsedProfile.skills?.length || 0})
              </label>
              <div className="flex flex-wrap gap-1.5">
                {parsedProfile.skills?.map((sk, idx) => (
                  <span key={idx} className="bg-slate-100 text-slate-800 text-xs font-medium px-2.5 py-1 rounded-lg border border-slate-200">
                    {sk}
                  </span>
                ))}
              </div>
            </div>

            {/* Inferred Domains */}
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Inferred Career Domains
              </label>
              <div className="flex flex-wrap gap-2">
                {parsedProfile.domains?.map((dom, idx) => (
                  <span key={idx} className="bg-brand-50 text-brand-700 border border-brand-200 text-xs font-semibold px-3 py-1 rounded-lg">
                    {dom}
                  </span>
                ))}
              </div>
            </div>

            {/* Inferred Recommended Roles */}
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Recommended Job Roles
              </label>
              <div className="flex flex-wrap gap-2">
                {parsedProfile.recommended_roles?.map((r, idx) => (
                  <span key={idx} className="bg-indigo-50 text-indigo-700 border border-indigo-200 text-xs font-semibold px-3 py-1 rounded-lg">
                    {r}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Preferences Configuration */}
          <div className="bg-white rounded-3xl border border-slate-200 p-6 shadow-sm space-y-6">
            <h4 className="font-bold text-navy-900 text-base flex items-center gap-2">
              <Sliders className="w-4 h-4 text-brand-600" />
              Customize Recommendation Preferences
            </h4>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Location Preference
                </label>
                <select
                  value={remotePreference}
                  onChange={(e) => setRemotePreference(e.target.value)}
                  className="w-full p-2.5 rounded-xl border border-slate-300 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-brand-500/20"
                >
                  <option value="any">Any (Remote, Hybrid, Onsite)</option>
                  <option value="remote">Remote Preferred</option>
                  <option value="hybrid">Hybrid</option>
                  <option value="onsite">Onsite Only</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Minimum Match Compatibility
                </label>
                <div className="flex items-center gap-3">
                  <input
                    type="range"
                    min="30"
                    max="90"
                    step="5"
                    value={minMatchScore}
                    onChange={(e) => setMinMatchScore(Number(e.target.value))}
                    className="flex-1 accent-brand-600 cursor-pointer"
                  />
                  <span className="text-sm font-bold text-navy-900 w-10 text-right">{minMatchScore}%</span>
                </div>
              </div>
            </div>

            <div className="flex justify-between items-center pt-4 border-t border-slate-100">
              <button
                onClick={() => setCurrentStep(0)}
                className="text-xs text-slate-500 hover:text-slate-800 font-semibold"
              >
                Re-upload Resume
              </button>
              <button
                onClick={handleConfirmProfile}
                className="px-8 py-3.5 bg-brand-600 hover:bg-brand-700 text-white font-bold text-sm rounded-xl shadow-md shadow-brand-500/25 flex items-center gap-2 transition-transform hover:scale-[1.02]"
              >
                <span>Find My Jobs</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
