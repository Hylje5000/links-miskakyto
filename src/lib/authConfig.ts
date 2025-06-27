import { isTestMode, msalTestConfig, testModeConfig } from './testConfig';

export const msalConfig = isTestMode ? msalTestConfig : {
  auth: {
    clientId: process.env.NEXT_PUBLIC_AZURE_CLIENT_ID || 'your-client-id',
    authority: `https://login.microsoftonline.com/${process.env.NEXT_PUBLIC_AZURE_TENANT_ID || 'your-tenant-id'}`,
    redirectUri: process.env.NEXT_PUBLIC_REDIRECT_URI || 'http://localhost:3000',
  },
  cache: {
    cacheLocation: 'localStorage',
    storeAuthStateInCookie: false,
  },
};

export const loginRequest = {
  scopes: ['openid', 'profile', 'email'],
};

export const apiRequest = {
  scopes: [`api://${process.env.NEXT_PUBLIC_AZURE_CLIENT_ID}/.default`],
};

// Test mode helpers
export const getTestModeUser = () => isTestMode ? testModeConfig.mockUser : null;
