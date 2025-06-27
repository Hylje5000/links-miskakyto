import axios from 'axios';
import { isTestMode, testModeConfig } from './testConfig';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  if (isTestMode) {
    // In test mode, add a mock token
    config.headers.Authorization = 'Bearer test-token';
  } else {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// API endpoints
export const linkAPI = {
  createLink: (data: { original_url: string; custom_short_code?: string; description?: string }) =>
    api.post('/api/links', data),
  
  getLinks: () => api.get('/api/links'),
  
  getLink: (id: string) => api.get(`/api/links/${id}`),
  
  updateLink: (id: string, data: { description?: string }) =>
    api.put(`/api/links/${id}`, data),
  
  deleteLink: (id: string) => api.delete(`/api/links/${id}`),
  
  getLinkAnalytics: (id: string) => api.get(`/api/links/${id}/analytics`),
};

export type Link = {
  id: string;
  original_url: string;
  short_code: string;
  short_url: string;
  description?: string;
  click_count: number;
  created_at: string;
  created_by: string;
  tenant_id: string;
};

export type Analytics = {
  link_id: string;
  click_count: number;
  recent_clicks: Array<{
    clicked_at: string;
    ip_address: string;
  }>;
};
