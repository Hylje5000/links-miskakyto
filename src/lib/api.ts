import axios from 'axios';
import { isTestMode, testModeConfig } from './testConfig';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Store MSAL instance for token retrieval
let msalInstance: any = null;

export const setMsalInstance = (instance: any) => {
  msalInstance = instance;
};

// Add auth token to requests
api.interceptors.request.use(async (config) => {
  if (isTestMode) {
    // In test mode, add a mock token
    config.headers.Authorization = 'Bearer test-token';
  } else if (msalInstance) {
    try {
      const accounts = msalInstance.getAllAccounts();
      
      if (accounts.length > 0) {
        try {
          // Get the account
          const account = accounts[0];
          
          // Use acquireTokenSilent to get ID token
          const response = await msalInstance.acquireTokenSilent({
            scopes: ['openid'], // Only request openid scope for ID token
            account: account,
            forceRefresh: false
          });
          
          if (response.idToken) {
            // Use the ID token for authentication
            config.headers.Authorization = `Bearer ${response.idToken}`;
            return config;
          }
        } catch (tokenError: any) {
          // Try interactive token acquisition if silent fails
          if (tokenError.errorCode === 'consent_required' || 
              tokenError.errorCode === 'interaction_required') {
            try {
              const interactiveResponse = await msalInstance.acquireTokenPopup({
                scopes: ['openid'], // Only openid scope for ID token
                account: accounts[0],
              });
              if (interactiveResponse.idToken) {
                config.headers.Authorization = `Bearer ${interactiveResponse.idToken}`;
                return config;
              }
            } catch (interactiveError) {
              console.error('Interactive token acquisition failed:', interactiveError);
            }
          }
        }
      }
    } catch (error) {
      console.error('Error in token acquisition:', error);
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
