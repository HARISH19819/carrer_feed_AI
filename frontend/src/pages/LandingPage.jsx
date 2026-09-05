import React from 'react';
import { 
  Sparkles, 
  Upload, 
  FileText, 
  Cpu, 
  CheckCircle2, 
  ArrowRight, 
  ShieldCheck, 
  Target, 
  TrendingUp, 
  Briefcase, 
  Compass, 
  ChevronRight,
  HelpCircle,
  Zap,
  Globe2,
  Lock
} from 'lucide-react';

export default function LandingPage({ setActivePage }) {
  const steps = [
    { num: '01', title: 'Upload Resume', desc: 'Accepts PDF or DOCX. Document parsers extract raw text with zero third-party leakage.', icon: FileText },
    { num: '02', title: 'Candidate Intelligence', desc: 'Extracts skills, infers career domains, normalizes aliases, and calculates profile strength.', icon: Cpu },
    { num: '03', title: 'Job Discovery & Dedup', desc: 'Discovers fresh opportunities from permitted APIs, normalizes titles, and deduplicates multi-source records.', icon: Globe2 },
    { num: '04', title: 'Domain Classification', desc: 'Classifies roles across 22 career taxonomy domains with experience level and skills requirements.', icon: Zap },
    { num: '05', title: 'Deterministic Match', desc: 'Calculates transparent compatibility using 7-dimension scoring + semantic embedding similarity.', icon: Target },
    { num: '06', title: 'Track & Apply', desc: 'Directs you to apply on the verified source employer page and track interview progress.', icon: Briefcase }
  ];

  const faqs = [
    {
      q: "Is JobFusion AI another job board?",
      a: "No. JobFusion AI is a unified career intelligence and recommendation layer. We aggregate, normalize, and match opportunities from permitted sources and direct you to the original external posting to apply."
    },
    {
      q: "How does the match scoring engine work?",
      a: "Scoring is deterministic and transparent: 30% Skill match, 20% Role match, 15% Domain alignment, 15% Experience match, 10% Education compatibility, 5% Location fit, and 5% Preferences, combined with semantic similarity. No unexplained black-box numbers."
    },
    {
      q: "Is my resume data kept private?",
      a: "Yes. Resumes are processed locally in your session and candidate profiles are stored securely in MongoDB Atlas with user-specific authorization. Raw resume data is never sold or broadcasted."
    },
    {
      q: "Can freshers and students use this?",
      a: "Absolutely. JobFusion AI specifically categorizes fresher, internship, and junior roles, highlighting entry-level requirements and actionable skill gap recommendations."
    }
  ];

  return (
    <div className="space-y-24 py-6">
      
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-8 pb-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-8">
          
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-brand-50 border border-brand-200 text-brand-700 text-xs font-semibold shadow-xs">
            <Sparkles className="w-3.5 h-3.5 text-brand-600 animate-spin" />
            <span>Autonomous Multi-Agent Career Intelligence</span>
          </div>

          {/* Main Title */}
          <div className="max-w-4xl mx-auto space-y-4">
            <h1 className="text-4xl sm:text-6xl font-extrabold text-navy-900 tracking-tight leading-[1.15]">
              One Resume. Every Opportunity. <br />
              <span className="bg-gradient-to-r from-brand-600 via-indigo-600 to-cyan-600 bg-clip-text text-transparent">
                One Intelligent Career Feed.
              </span>
            </h1>
            <p className="text-lg sm:text-xl text-slate-600 max-w-2xl mx-auto leading-relaxed font-normal">
              JobFusion AI discovers, understands, and ranks job opportunities from multiple sources according to your candidate profile.
            </p>
          </div>

          {/* Action CTAs */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-2">
            <button
              onClick={() => setActivePage('onboarding')}
              className="w-full sm:w-auto px-8 py-4 bg-brand-600 hover:bg-brand-700 active:bg-brand-800 text-white font-bold text-base rounded-2xl shadow-xl shadow-brand-500/25 flex items-center justify-center gap-2.5 transition-all hover:scale-[1.02]"
            >
              <Upload className="w-5 h-5" />
              <span>Build My Career Profile</span>
            </button>
            
            <button
              onClick={() => setActivePage('jobs')}
              className="w-full sm:w-auto px-8 py-4 bg-white hover:bg-slate-50 text-slate-800 font-bold text-base rounded-2xl border border-slate-300 shadow-sm flex items-center justify-center gap-2 transition-all hover:border-slate-400"
            >
              <Compass className="w-5 h-5 text-slate-500" />
              <span>Explore Jobs</span>
            </button>
          </div>

          {/* Visual Pipeline Progression Hero Graphic */}
          <div className="pt-12 max-w-5xl mx-auto">
            <div className="bg-white rounded-3xl border border-slate-200/80 p-6 sm:p-8 shadow-xl relative">
              <div className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-6 flex items-center justify-between">
                <span>Autonomous Agent Orchestration Stream</span>
                <span className="text-emerald-600 flex items-center gap-1">● System Active</span>
              </div>
              
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3">
                {[
                  { name: 'Resume', sub: 'PDF / DOCX', color: 'border-blue-200 bg-blue-50/50 text-blue-700' },
                  { name: 'AI Profile', sub: 'Skills & Roles', color: 'border-indigo-200 bg-indigo-50/50 text-indigo-700' },
                  { name: 'Job Sources', sub: 'Discovery APIs', color: 'border-cyan-200 bg-cyan-50/50 text-cyan-700' },
                  { name: 'Classifier', sub: '22 Domains', color: 'border-purple-200 bg-purple-50/50 text-purple-700' },
                  { name: 'Matching Engine', sub: '7-D Scoring', color: 'border-emerald-200 bg-emerald-50/50 text-emerald-700' },
                  { name: 'Ranked Feed', sub: 'Explainable Fits', color: 'border-amber-200 bg-amber-50/50 text-amber-700' }
                ].map((item, idx) => (
                  <div key={idx} className={`p-4 rounded-2xl border text-center ${item.color} flex flex-col justify-center items-center`}>
                    <span className="text-xs font-bold block mb-1 text-slate-900">{item.name}</span>
                    <span className="text-[11px] opacity-75 font-medium">{item.sub}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Problem & Solution Comparison */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          
          {/* The Problem */}
          <div className="bg-rose-50/50 border border-rose-100 rounded-3xl p-8">
            <span className="text-xs font-bold text-rose-700 tracking-wider uppercase bg-rose-100 px-3 py-1 rounded-full">
              The Problem Today
            </span>
            <h3 className="text-2xl font-bold text-slate-900 mt-4 mb-4">Fragmented, Monopolistic Job Search</h3>
            <ul className="space-y-3 text-sm text-slate-700">
              <li className="flex items-start gap-2">
                <span className="text-rose-500 font-bold">✕</span>
                <span>Job seekers search across dozens of separate sites (LinkedIn, Naukri, Internshala, Indeed).</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-rose-500 font-bold">✕</span>
                <span>Platforms push listings from their own paid ecosystem rather than what truly fits your skills.</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-rose-500 font-bold">✕</span>
                <span>Black-box AI scores leave candidates confused about why they matched or why they were rejected.</span>
              </li>
            </ul>
          </div>

          {/* The Solution */}
          <div className="bg-emerald-50/50 border border-emerald-100 rounded-3xl p-8">
            <span className="text-xs font-bold text-emerald-700 tracking-wider uppercase bg-emerald-100 px-3 py-1 rounded-full">
              The JobFusion AI Solution
            </span>
            <h3 className="text-2xl font-bold text-slate-900 mt-4 mb-4">Unified Career Intelligence Layer</h3>
            <ul className="space-y-3 text-sm text-slate-700">
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
                <span>One resume upload populates an autonomous career intelligence profile.</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
                <span>Aggregates, normalizes, and deduplicates opportunities across all permitted sources.</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
                <span>Transparent scoring explains strong skill matches and actionable missing skills.</span>
              </li>
            </ul>
          </div>
        </div>
      </section>

      {/* Multi-Agent Architecture */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-12 space-y-3">
          <span className="text-xs font-bold uppercase tracking-widest text-brand-600 bg-brand-50 px-3 py-1 rounded-full">
            Autonomous Multi-Agent Architecture
          </span>
          <h2 className="text-3xl font-extrabold text-navy-900">How JobFusion AI Works</h2>
          <p className="text-sm text-slate-600">
            Four specialized intelligent agents coordinate to discover, structure, and rank opportunities for you.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {steps.map((st, i) => {
            const Icon = st.icon;
            return (
              <div key={i} className="bg-white rounded-3xl border border-slate-200 p-6 shadow-xs hover:shadow-md transition-all space-y-3">
                <div className="flex items-center justify-between">
                  <div className="w-12 h-12 rounded-2xl bg-brand-50 border border-brand-100 flex items-center justify-center text-brand-600">
                    <Icon className="w-6 h-6" />
                  </div>
                  <span className="text-xl font-black text-slate-200">{st.num}</span>
                </div>
                <h4 className="font-bold text-lg text-navy-900">{st.title}</h4>
                <p className="text-xs text-slate-600 leading-relaxed">{st.desc}</p>
              </div>
            );
          })}
        </div>
      </section>

      {/* Frequently Asked Questions */}
      <section className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-10">
          <h2 className="text-2xl sm:text-3xl font-bold text-navy-900">Frequently Asked Questions</h2>
        </div>
        <div className="space-y-4">
          {faqs.map((faq, idx) => (
            <div key={idx} className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
              <h4 className="font-bold text-base text-navy-900 flex items-center gap-2 mb-2">
                <HelpCircle className="w-4 h-4 text-brand-600" />
                {faq.q}
              </h4>
              <p className="text-sm text-slate-600 leading-relaxed pl-6">{faq.a}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Bottom CTA Banner */}
      <section className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-gradient-to-r from-brand-700 via-brand-600 to-indigo-700 rounded-3xl p-8 sm:p-12 text-center text-white shadow-xl space-y-6">
          <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight">
            Ready to find the opportunities that truly fit you?
          </h2>
          <p className="text-brand-100 text-sm sm:text-base max-w-xl mx-auto">
            Upload your resume once and experience an intelligent, personalized career feed.
          </p>
          <div className="pt-2">
            <button
              onClick={() => setActivePage('onboarding')}
              className="px-8 py-4 bg-white hover:bg-slate-100 text-brand-700 font-bold rounded-2xl shadow-lg transition-transform hover:scale-105 inline-flex items-center gap-2"
            >
              <Upload className="w-5 h-5 text-brand-700" />
              <span>Get Started Free</span>
            </button>
          </div>
        </div>
      </section>

    </div>
  );
}
