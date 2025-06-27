'use client';

import { useMsal } from '@azure/msal-react';
import { LogOut, User } from 'lucide-react';
import { isTestMode, testModeConfig } from '@/lib/testConfig';

export function Header() {
  const { instance, accounts } = useMsal();
  const account = isTestMode ? testModeConfig.mockUser : accounts[0];

  const handleLogout = () => {
    if (isTestMode) {
      // In test mode, just reload the page or clear test state
      window.location.reload();
    } else {
      instance.logoutPopup().catch((e) => {
        console.error(e);
      });
    }
  };

  return (
    <header className="bg-white shadow border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          <div className="flex items-center space-x-3">
            <div className="text-lg font-semibold text-gray-900">
              Link Shortener
            </div>
            {isTestMode && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                Test Mode
              </span>
            )}
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <User className="h-4 w-4" />
              <span>
                {isTestMode 
                  ? (account as any)?.name || (account as any)?.email 
                  : (account as any)?.name || (account as any)?.username
                }
              </span>
            </div>
            
            <button
              onClick={handleLogout}
              className="flex items-center space-x-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
            >
              <LogOut className="h-4 w-4" />
              <span>Sign out</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
