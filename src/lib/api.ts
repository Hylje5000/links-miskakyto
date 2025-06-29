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
    console.log('🧪 Using test mode token');
  } else if (msalInstance) {
    try {
      const accounts = msalInstance.getAllAccounts();
      console.log('📧 Available accounts:', accounts.length);
      
      if (accounts.length > 0) {
        try {
          // Use ID token for authentication - much simpler!
          const response = await msalInstance.acquireTokenSilent({
            scopes: ['openid', 'profile', 'email'],
            account: accounts[0],
          });
          
          if (response.idToken) {
            config.headers.Authorization = `Bearer ${response.idToken}`;
            console.log('🔑 Using ID token for authentication');
            console.log('👤 User:', response.account?.name);
            return config;
          } else {
            console.error('❌ No ID token received');
          }
        } catch (tokenError: any) {
          console.error('❌ Token acquisition failed:', tokenError);
          
          // Try interactive token acquisition if silent fails
          if (tokenError.errorCode === 'consent_required' || 
              tokenError.errorCode === 'interaction_required') {
            console.log('🔐 Attempting interactive token acquisition...');
            try {
              const interactiveResponse = await msalInstance.acquireTokenPopup({
                scopes: ['openid', 'profile', 'email'],
                account: accounts[0],
              });
              if (interactiveResponse.idToken) {
                config.headers.Authorization = `Bearer ${interactiveResponse.idToken}`;
                console.log('🔑 Using interactively acquired ID token');
                return config;
              }
            } catch (interactiveError) {
              console.error('❌ Interactive token acquisition failed:', interactiveError);
            }
          }
        }

        console.error('❌ Failed to acquire ID token');
      } else {
        console.warn('⚠️ No accounts found, user might need to sign in');
      }
    } catch (error) {
      console.error('💥 Error in token acquisition:', error);
    }
  } else {
    console.warn('⚠️ MSAL instance not available');
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
