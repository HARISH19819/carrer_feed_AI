import React, { useState, useEffect } from 'react';
import { useAuth } from './context/AuthContext';
import Navbar from './components/Navbar';
import Footer from './components/Footer';

// Pages
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import OnboardingPage from './pages/OnboardingPage';
import DashboardPage from './pages/DashboardPage';
import AllJobsPage from './pages/AllJobsPage';
import MyMatchesPage from './pages/MyMatchesPage';
import SavedJobsPage from './pages/SavedJobsPage';
import SkillGapsPage from './pages/SkillGapsPage';
import ProfilePage from './pages/ProfilePage';
import AdminPage from './pages/AdminPage';

export default function App() {
  const { isAuthenticated, isAdmin, loading } = useAuth();
  const [activePage, setActivePage] = useState('landing');

  // Automatic redirect based on authentication state on initial load
  useEffect(() => {
    if (!loading) {
      if (isAuthenticated) {
        if (activePage === 'landing' || activePage === 'login' || activePage === 'register') {
          setActivePage('dashboard');
        }
      }
    }
  }, [isAuthenticated, loading]);

  // Protected route enforcement
  const renderPage = () => {
    if (loading) {
      return (
        <div className="min-h-[60vh] flex items-center justify-center">
          <div className="w-8 h-8 rounded-full border-4 border-brand-200 border-t-brand-600 animate-spin" />
        </div>
      );
    }

    switch (activePage) {
      case 'landing':
        return <LandingPage setActivePage={setActivePage} />;
      case 'login':
        return <LoginPage setActivePage={setActivePage} />;
      case 'register':
        return <RegisterPage setActivePage={setActivePage} />;
      case 'onboarding':
        return isAuthenticated ? (
          <OnboardingPage setActivePage={setActivePage} />
        ) : (
          <LoginPage setActivePage={setActivePage} />
        );
      case 'dashboard':
        return isAuthenticated ? (
          <DashboardPage setActivePage={setActivePage} />
        ) : (
          <LoginPage setActivePage={setActivePage} />
        );
      case 'jobs':
        return <AllJobsPage setActivePage={setActivePage} />;
      case 'matches':
        return isAuthenticated ? (
          <MyMatchesPage setActivePage={setActivePage} />
        ) : (
          <LoginPage setActivePage={setActivePage} />
        );
      case 'saved':
        return isAuthenticated ? (
          <SavedJobsPage setActivePage={setActivePage} />
        ) : (
          <LoginPage setActivePage={setActivePage} />
        );
      case 'skill-gaps':
        return isAuthenticated ? (
          <SkillGapsPage setActivePage={setActivePage} />
        ) : (
          <LoginPage setActivePage={setActivePage} />
        );
      case 'profile':
        return isAuthenticated ? (
          <ProfilePage setActivePage={setActivePage} />
        ) : (
          <LoginPage setActivePage={setActivePage} />
        );
      case 'admin':
        return isAuthenticated && isAdmin ? (
          <AdminPage setActivePage={setActivePage} />
        ) : (
          <DashboardPage setActivePage={setActivePage} />
        );
      default:
        return <LandingPage setActivePage={setActivePage} />;
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900 selection:bg-brand-500 selection:text-white">
      <Navbar activePage={activePage} setActivePage={setActivePage} />
      <main className="flex-1">
        {renderPage()}
      </main>
      <Footer setActivePage={setActivePage} />
    </div>
  );
}
