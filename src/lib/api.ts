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
        // PRIORITY 1: Try to get an access token for the custom API
        try {
          const apiRequest = {
            scopes: [`${process.env.NEXT_PUBLIC_AZURE_CLIENT_ID}/.default`],
            account: accounts[0],
          };
          const apiResponse = await msalInstance.acquireTokenSilent(apiRequest);
          if (apiResponse.accessToken) {
            config.headers.Authorization = `Bearer ${apiResponse.accessToken}`;
            console.log('🔑 Using access token for custom API authentication');
            console.log('🎯 Token audience should be:', process.env.NEXT_PUBLIC_AZURE_CLIENT_ID);
            return config;
          }
        } catch (accessTokenError: any) {
          console.warn('❌ Custom API access token acquisition failed:', accessTokenError);
          
          // If the error is about consent or permissions, try interactive token acquisition
          if (accessTokenError.errorCode === 'consent_required' || 
              accessTokenError.errorCode === 'interaction_required') {
            console.log('🔐 Attempting interactive token acquisition...');
            try {
              const interactiveResponse = await msalInstance.acquireTokenPopup({
                scopes: [`${process.env.NEXT_PUBLIC_AZURE_CLIENT_ID}/.default`],
                account: accounts[0],
              });
              if (interactiveResponse.accessToken) {
                config.headers.Authorization = `Bearer ${interactiveResponse.accessToken}`;
                console.log('🔑 Using interactively acquired access token');
                return config;
              }
            } catch (interactiveError) {
              console.error('❌ Interactive token acquisition failed:', interactiveError);
            }
          }
        }

        // FALLBACK: Try to get an ID token (for backwards compatibility)
        try {
          const basicRequest = {
            scopes: ['openid', 'profile', 'email'],
            account: accounts[0],
          };
          const basicResponse = await msalInstance.acquireTokenSilent(basicRequest);
          if (basicResponse.idToken) {
            config.headers.Authorization = `Bearer ${basicResponse.idToken}`;
            console.log('⚠️ Using ID token as fallback (may not work with API)');
            console.log('💡 Consider ensuring your Azure AD app registration exposes an API');
            return config;
          }
        } catch (idTokenError) {
          console.warn('ID token acquisition also failed:', idTokenError);
        }

        console.error('❌ Failed to acquire any usable token');
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
