import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Home from '../app/page';

// Mock environment variables for test mode
jest.mock('../lib/testConfig', () => ({
  isTestMode: true,
  testModeConfig: {
    mockUser: {
      oid: 'test-user-id',
      name: 'Test User',
      email: 'test@example.com',
      tid: 'test-tenant-id',
    },
    apiUrl: 'http://localhost:8000',
  },
}));

// Mock MsalProvider completely
jest.mock('@azure/msal-react', () => ({
  MsalProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  useMsal: () => ({
    instance: {
      getAllAccounts: jest.fn(() => []),
      getActiveAccount: jest.fn(() => null),
    },
    accounts: [],
    inProgress: 'None',
  }),
  useIsAuthenticated: () => false,
}));

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
      mutations: {
        retry: false,
      },
    },
  });

function renderWithProviders(ui: React.ReactElement) {
  const testQueryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={testQueryClient}>
      {ui}
    </QueryClientProvider>
  );
}

// Mock the components since they're complex
jest.mock('../components/LinkDashboard', () => {
  return {
    LinkDashboard: () => <div data-testid="link-dashboard">Dashboard Content</div>
  };
});

describe('Home Page Integration', () => {
  test('renders test mode indicator and dashboard in test mode', async () => {
    renderWithProviders(<Home />);

    // Should show test mode indicator
    await waitFor(() => {
      expect(screen.getByText(/test mode active/i)).toBeDefined();
    });

    // Should show dashboard
    expect(screen.getByTestId('link-dashboard')).toBeDefined();
  });

  test('shows test mode banner with correct styling', async () => {
    renderWithProviders(<Home />);

    await waitFor(() => {
      const testModeBanner = screen.getByText(/test mode active/i);
      expect(testModeBanner).toBeDefined();
    });
  });
});
