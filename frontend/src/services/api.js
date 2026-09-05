// Dynamic API Base URL supporting production environment variables
const API_BASE = (import.meta.env && import.meta.env.VITE_API_BASE_URL)
  ? import.meta.env.VITE_API_BASE_URL
  : (typeof window !== 'undefined' && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1')
    ? '/api'
    : 'http://localhost:8000/api';

class ApiClient {
  constructor() {
    this.token = typeof localStorage !== 'undefined' ? localStorage.getItem('jf_token') : null;
  }

  setToken(token) {
    this.token = token;
    if (typeof localStorage !== 'undefined') {
      if (token) {
        localStorage.setItem('jf_token', token);
      } else {
        localStorage.removeItem('jf_token');
      }
    }
  }

  getHeaders(isFormData = false) {
    const headers = {};
    if (!isFormData) {
      headers['Content-Type'] = 'application/json';
    }
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    return headers;
  }

  async request(endpoint, options = {}) {
    const isFormData = options.body instanceof FormData;
    const config = {
      ...options,
      headers: {
        ...this.getHeaders(isFormData),
        ...(options.headers || {})
      }
    };

    let response;
    try {
      response = await fetch(`${API_BASE}${endpoint}`, config);
    } catch (networkErr) {
      console.warn(`Network connection failure at ${endpoint}:`, networkErr);
      throw new Error('Unable to connect to the JobFusion server. Please verify your network connection or verify the backend service is running.');
    }

    if (response.status === 401) {
      // Clear token if expired or revoked
      this.setToken(null);
      if (typeof window !== 'undefined' && 
          !window.location.pathname.includes('/login') && 
          !window.location.pathname.includes('/register') && 
          window.location.pathname !== '/') {
        window.location.href = '/login';
      }
    }

    if (!response.ok) {
      let errorDetail = 'An error occurred';
      try {
        const errorData = await response.json();
        errorDetail = errorData.detail || errorDetail;
      } catch (e) {
        errorDetail = response.statusText || 'Server error';
      }
      throw new Error(errorDetail);
    }

    // Return json if available
    try {
      return await response.json();
    } catch {
      return null;
    }
  }

  // Auth
  async register(name, email, password) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ name, email, password })
    });
  }

  async login(email, password) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
  }

  async getMe() {
    return this.request('/auth/me');
  }

  async logout() {
    this.setToken(null);
  }

  // Profile
  async getProfile() {
    return this.request('/profile');
  }

  async uploadResume(file) {
    const formData = new FormData();
    formData.append('file', file);
    return this.request('/profile/resume', {
      method: 'POST',
      body: formData
    });
  }

  async updateProfile(updates) {
    return this.request('/profile', {
      method: 'PUT',
      body: JSON.stringify(updates)
    });
  }

  async reanalyzeProfile() {
    return this.request('/profile/reanalyze', { method: 'POST' });
  }

  // Jobs
  async getJobs(params = {}) {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '' && v !== 'all') {
        query.append(k, v);
      }
    });
    return this.request(`/jobs?${query.toString()}`);
  }

  async getJobById(jobId) {
    return this.request(`/jobs/${jobId}`);
  }

  // Matches
  async getMatches(params = {}) {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '' && v !== 'all') {
        query.append(k, v);
      }
    });
    return this.request(`/matches?${query.toString()}`);
  }

  async getMatchById(jobId) {
    return this.request(`/matches/${jobId}`);
  }

  // Saved Jobs
  async getSavedJobs() {
    return this.request('/saved');
  }

  async saveJob(jobId) {
    return this.request(`/saved/${jobId}`, { method: 'POST' });
  }

  async unsaveJob(jobId) {
    return this.request(`/saved/${jobId}`, { method: 'DELETE' });
  }

  // Applications
  async getApplications() {
    return this.request('/applications');
  }

  async trackApplication(jobId, status = 'Applied', notes = null) {
    return this.request(`/applications/${jobId}`, {
      method: 'POST',
      body: JSON.stringify({ job_id: jobId, status, notes })
    });
  }

  async updateApplication(applicationId, status, notes = null) {
    return this.request(`/applications/${applicationId}`, {
      method: 'PATCH',
      body: JSON.stringify({ status, notes })
    });
  }

  async getApplicationStats() {
    return this.request('/applications/stats/summary');
  }

  // Skill Gaps
  async getSkillGaps() {
    return this.request('/skill-gaps');
  }

  // Pipeline & Agents
  async getPipelineStatus() {
    return this.request('/pipeline/status');
  }

  async runPipeline(agent = 'all') {
    return this.request(`/pipeline/run?agent=${agent}`, { method: 'POST' });
  }

  // Admin
  async getAdminStats() {
    return this.request('/admin/stats');
  }

  async getAdminSources() {
    return this.request('/admin/sources');
  }

  async updateAdminSource(adapterKey, payload) {
    return this.request(`/admin/sources/${adapterKey}`, {
      method: 'PATCH',
      body: JSON.stringify(payload)
    });
  }

  async triggerSourceSync(adapterKey) {
    return this.request(`/admin/sources/${adapterKey}/run`, { method: 'POST' });
  }
}

export const api = new ApiClient();
