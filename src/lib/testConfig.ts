export const isTestMode = process.env.NEXT_PUBLIC_TEST_MODE === 'true';

export const testModeConfig = {
  // Mock user data for test mode
  mockUser: {
    oid: 'test-user-id',
    name: 'Test User',
    email: 'test@example.com',
    tid: 'test-tenant-id',
  },
  
  // Test mode API base URL
  apiUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
};

export const msalTestConfig = {
  auth: {
    clientId: 'test-client-id',
    authority: 'https://login.microsoftonline.com/test-tenant-id',
    redirectUri: 'http://localhost:3000',
  },
  cache: {
    cacheLocation: 'localStorage',
    storeAuthStateInCookie: false,
  },
};
