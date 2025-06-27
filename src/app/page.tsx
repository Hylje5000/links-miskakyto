'use client';

import { useMsal, useIsAuthenticated } from '@azure/msal-react';
import { loginRequest } from '@/lib/authConfig';
import { isTestMode } from '@/lib/testConfig';
import { LinkDashboard } from '@/components/LinkDashboard';
import { Link2, Lock, Users, BarChart3, TestTube } from 'lucide-react';

export default function Home() {
  const { instance } = useMsal();
  const isAuthenticated = useIsAuthenticated();

  const handleLogin = () => {
    instance.loginPopup(loginRequest).catch((e) => {
      console.error(e);
    });
  };

  // In test mode, always show as authenticated
  const shouldShowDashboard = isTestMode || isAuthenticated;

  if (!shouldShowDashboard) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="flex items-center justify-center min-h-screen">
          <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-xl shadow-lg">
            <div className="text-center">
              <div className="flex justify-center mb-4">
                <Link2 className="h-12 w-12 text-blue-600" />
              </div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Link Shortener
              </h1>
              <p className="text-gray-600">
                Secure URL shortening with enterprise authentication
              </p>
            </div>

            <div className="space-y-4">
              <div className="flex items-center space-x-3 text-sm text-gray-600">
                <Lock className="h-4 w-4 text-green-500" />
                <span>Entra ID Authentication</span>
              </div>
              <div className="flex items-center space-x-3 text-sm text-gray-600">
                <BarChart3 className="h-4 w-4 text-blue-500" />
                <span>Click Tracking & Analytics</span>
              </div>
              <div className="flex items-center space-x-3 text-sm text-gray-600">
                <Users className="h-4 w-4 text-purple-500" />
                <span>Tenant-based Link Management</span>
              </div>
            </div>

            <button
              onClick={handleLogin}
              className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
            >
              Sign in with Microsoft
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <>
      {isTestMode && (
        <div className="bg-yellow-100 border-l-4 border-yellow-500 p-4">
          <div className="flex items-center">
            <TestTube className="h-5 w-5 text-yellow-500 mr-2" />
            <span className="text-yellow-700 font-medium">Test Mode Active</span>
            <span className="text-yellow-600 ml-2 text-sm">
              Authentication is bypassed for development
            </span>
          </div>
        </div>
      )}
      <LinkDashboard />
    </>
  );
}
