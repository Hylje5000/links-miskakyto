import axios from 'axios';
import { isTestMode } from './testConfig';
import { PublicClientApplication } from '@azure/msal-browser';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Store MSAL instance for token retrieval  
let msalInstance: PublicClientApplication | null = null;

export const setMsalInstance = (instance: PublicClientApplication) => {
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
          });
          
          if (response.idToken) {
            // Use the ID token for authentication
            config.headers.Authorization = `Bearer ${response.idToken}`;
            return config;
          }
        } catch (tokenError: unknown) {
          // Try interactive token acquisition if silent fails
          if ((tokenError as { errorCode?: string })?.errorCode === 'consent_required' || 
              (tokenError as { errorCode?: string })?.errorCode === 'interaction_required') {
            try {
              const interactiveResponse = await msalInstance.acquireTokenPopup({
                scopes: ['openid'], // Only openid scope for ID token
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
      return Promise.reject(error);
    }
  }

  if (!config.headers.Authorization && !isTestMode) {
    return Promise.reject(new Error('No auth token available'));
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
  total_clicks: number;
  clicks_today: number;
  clicks_this_week: number;
  clicks_this_month: number;
  recent_clicks: Array<{
    id?: string;
    clicked_at: string;
    ip_address: string;
    user_agent?: string;
  }>;
};
