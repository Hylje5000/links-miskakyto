import { isTestMode, testModeConfig } from '../lib/testConfig';

describe('Test Mode Configuration', () => {
  test('isTestMode should be boolean', () => {
    expect(typeof isTestMode).toBe('boolean');
  });

  test('testModeConfig should have required properties', () => {
    expect(testModeConfig).toHaveProperty('mockUser');
    expect(testModeConfig).toHaveProperty('apiUrl');
    expect(testModeConfig.mockUser).toHaveProperty('oid');
    expect(testModeConfig.mockUser).toHaveProperty('name');
    expect(testModeConfig.mockUser).toHaveProperty('email');
    expect(testModeConfig.mockUser).toHaveProperty('tid');
  });

  test('mock user should have valid data', () => {
    const { mockUser } = testModeConfig;
    expect(mockUser.oid).toBe('test-user-id');
    expect(mockUser.name).toBe('Test User');
    expect(mockUser.email).toBe('test@example.com');
    expect(mockUser.tid).toBe('test-tenant-id');
  });
});
