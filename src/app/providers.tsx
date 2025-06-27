'use client';

import { MsalProvider } from '@azure/msal-react';
import { PublicClientApplication } from '@azure/msal-browser';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { msalConfig } from '@/lib/authConfig';
import { useState } from 'react';

const msalInstance = new PublicClientApplication(msalConfig);

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 1000 * 60 * 5, // 5 minutes
        gcTime: 1000 * 60 * 30, // 30 minutes
      },
    },
  }));

  return (
    <MsalProvider instance={msalInstance}>
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    </MsalProvider>
  );
}
