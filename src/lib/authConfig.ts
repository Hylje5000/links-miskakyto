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
  scopes: ['openid'], // Only request openid scope to ensure we get ID token
};

// Remove the apiRequest - we'll use ID tokens instead
// export const apiRequest = {
//   scopes: [`${process.env.NEXT_PUBLIC_AZURE_CLIENT_ID}/.default`],
// };

// Test mode helpers
export const getTestModeUser = () => isTestMode ? testModeConfig.mockUser : null;
