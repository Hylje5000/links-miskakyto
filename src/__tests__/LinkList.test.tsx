import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { LinkList } from '../components/LinkList';
import type { Link } from '../lib/api';

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

function renderWithQueryClient(ui: React.ReactElement) {
  const testQueryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={testQueryClient}>
      {ui}
    </QueryClientProvider>
  );
}

const mockLinks: Link[] = [
  {
    id: '1',
    original_url: 'https://example.com/1',
    short_code: 'abc123',
    short_url: 'http://localhost:8000/abc123',
    description: 'Test link 1',
    click_count: 5,
    created_at: '2023-01-01T00:00:00Z',
    created_by: 'user1',
    tenant_id: 'tenant1',
  },
  {
    id: '2',
    original_url: 'https://example.com/2',
    short_code: 'def456',
    short_url: 'http://localhost:8000/def456',
    description: 'Test link 2',
    click_count: 10,
    created_at: '2023-01-02T00:00:00Z',
    created_by: 'user1',
    tenant_id: 'tenant1',
  },
];

describe('LinkList', () => {
  const mockOnDelete = jest.fn();
  const mockOnViewAnalytics = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders loading state', () => {
    renderWithQueryClient(
      <LinkList 
        links={[]} 
        isLoading={true} 
        onDelete={mockOnDelete} 
        onViewAnalytics={mockOnViewAnalytics} 
      />
    );

    expect(screen.getByTestId('loading-spinner')).toBeDefined();
  });

  test('renders empty state when no links', () => {
    renderWithQueryClient(
      <LinkList 
        links={[]} 
        isLoading={false} 
        onDelete={mockOnDelete} 
        onViewAnalytics={mockOnViewAnalytics} 
      />
    );

    expect(screen.getByText(/no links yet/i)).toBeDefined();
    expect(screen.getByText(/create your first short link/i)).toBeDefined();
  });

  test('renders links correctly', () => {
    renderWithQueryClient(
      <LinkList 
        links={mockLinks} 
        isLoading={false} 
        onDelete={mockOnDelete} 
        onViewAnalytics={mockOnViewAnalytics} 
      />
    );

    expect(screen.getByText('Test link 1')).toBeDefined();
    expect(screen.getByText('Test link 2')).toBeDefined();
    expect(screen.getByText('5 clicks')).toBeDefined();
    expect(screen.getByText('10 clicks')).toBeDefined();
  });

  test('displays link count in header', () => {
    renderWithQueryClient(
      <LinkList 
        links={mockLinks} 
        isLoading={false} 
        onDelete={mockOnDelete} 
        onViewAnalytics={mockOnViewAnalytics} 
      />
    );

    expect(screen.getByText('2')).toBeDefined(); // Link count badge
  });

  test('renders short URLs as clickable links', () => {
    renderWithQueryClient(
      <LinkList 
        links={mockLinks} 
        isLoading={false} 
        onDelete={mockOnDelete} 
        onViewAnalytics={mockOnViewAnalytics} 
      />
    );

    const shortLink1 = screen.getByText('http://localhost:8000/abc123');
    const shortLink2 = screen.getByText('http://localhost:8000/def456');
    
    expect(shortLink1.closest('a')).toHaveAttribute('href', 'http://localhost:8000/abc123');
    expect(shortLink2.closest('a')).toHaveAttribute('href', 'http://localhost:8000/def456');
  });

  test('renders action buttons for each link', () => {
    renderWithQueryClient(
      <LinkList 
        links={mockLinks} 
        isLoading={false} 
        onDelete={mockOnDelete} 
        onViewAnalytics={mockOnViewAnalytics} 
      />
    );

    const analyticsButtons = screen.getAllByText('Analytics');
    const deleteButtons = screen.getAllByText('Delete');
    
    expect(analyticsButtons).toHaveLength(2);
    expect(deleteButtons).toHaveLength(2);
  });
});
