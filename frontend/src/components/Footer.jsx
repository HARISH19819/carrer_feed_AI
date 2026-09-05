import React from 'react';
import { Sparkles, Shield, Cpu, RefreshCw, ExternalLink } from 'lucide-react';

export default function Footer({ setActivePage }) {
  return (
    <footer className="bg-white border-t border-slate-200 mt-20 pt-12 pb-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          
          {/* Col 1 */}
          <div className="space-y-4 md:col-span-1">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center text-white">
                <Sparkles className="w-4 h-4" />
              </div>
              <span className="font-bold text-lg text-navy-900">JobFusion AI</span>
            </div>
            <p className="text-sm text-slate-500 leading-relaxed">
              Autonomous multi-agent career intelligence platform. One resume, every opportunity, personalized recommendations with transparent explainability.
            </p>
          </div>

          {/* Col 2 */}
          <div>
            <h4 className="font-semibold text-sm text-slate-900 mb-3 uppercase tracking-wider">Candidate Feed</h4>
            <ul className="space-y-2 text-sm text-slate-600">
              <li><button onClick={() => setActivePage('dashboard')} className="hover:text-brand-600">Dashboard</button></li>
              <li><button onClick={() => setActivePage('jobs')} className="hover:text-brand-600">Explore All Jobs</button></li>
              <li><button onClick={() => setActivePage('matches')} className="hover:text-brand-600">Personalized Matches</button></li>
              <li><button onClick={() => setActivePage('skill-gaps')} className="hover:text-brand-600">Skill Gap Insights</button></li>
            </ul>
          </div>

          {/* Col 3 */}
          <div>
            <h4 className="font-semibold text-sm text-slate-900 mb-3 uppercase tracking-wider">Core Agents</h4>
            <ul className="space-y-2 text-sm text-slate-600">
              <li className="flex items-center gap-1.5"><Cpu className="w-3.5 h-3.5 text-brand-500" /> Scanner Agent</li>
              <li className="flex items-center gap-1.5"><Cpu className="w-3.5 h-3.5 text-indigo-500" /> Classifier Agent</li>
              <li className="flex items-center gap-1.5"><Cpu className="w-3.5 h-3.5 text-purple-500" /> Profile Agent</li>
              <li className="flex items-center gap-1.5"><Cpu className="w-3.5 h-3.5 text-emerald-500" /> Match Agent</li>
              <li className="flex items-center gap-1.5"><RefreshCw className="w-3.5 h-3.5 text-amber-500" /> Pipeline Orchestrator</li>
            </ul>
          </div>

          {/* Col 4 */}
          <div>
            <h4 className="font-semibold text-sm text-slate-900 mb-3 uppercase tracking-wider">Engineering Guarantees</h4>
            <div className="space-y-2.5 text-xs text-slate-500">
              <div className="flex items-start gap-2">
                <Shield className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <span>Zero-Cost Infrastructure: Runs on free-tier compute with local embeddings & deterministic scoring.</span>
              </div>
              <div className="flex items-start gap-2">
                <ExternalLink className="w-4 h-4 text-brand-600 shrink-0 mt-0.5" />
                <span>Source Transparency: Every job directs you to apply at the original verified source posting.</span>
              </div>
            </div>
          </div>
        </div>

        <div className="border-t border-slate-100 pt-6 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400 gap-2">
          <p>© {new Date().getFullYear()} JobFusion AI Platform. Built with FastAPI, MongoDB, React, and Scikit-Learn.</p>
          <p className="font-medium text-slate-500">Tagline: "One Resume. Every Opportunity. One Intelligent Career Feed."</p>
        </div>
      </div>
    </footer>
  );
}
