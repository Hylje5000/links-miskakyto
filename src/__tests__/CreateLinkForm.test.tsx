import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { CreateLinkForm } from '../components/CreateLinkForm';

// Mock the API
jest.mock('../lib/api', () => ({
  linkAPI: {
    createLink: jest.fn(),
  },
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

function renderWithQueryClient(ui: React.ReactElement) {
  const testQueryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={testQueryClient}>
      {ui}
    </QueryClientProvider>
  );
}

describe('CreateLinkForm', () => {
  const mockOnSubmit = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders form elements correctly', () => {
    renderWithQueryClient(
      <CreateLinkForm onSubmit={mockOnSubmit} isLoading={false} />
    );

    expect(screen.getByLabelText(/original url/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/custom short code/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /create short link/i })).toBeInTheDocument();
  });

  test('submits form with valid data', async () => {
    const user = userEvent.setup();
    
    renderWithQueryClient(
      <CreateLinkForm onSubmit={mockOnSubmit} isLoading={false} />
    );

    const urlInput = screen.getByLabelText(/original url/i);
    const submitButton = screen.getByRole('button', { name: /create short link/i });

    await user.type(urlInput, 'https://example.com');
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        original_url: 'https://example.com',
        custom_short_code: undefined,
        description: undefined,
      });
    });
  });

  test('submits form with all fields filled', async () => {
    const user = userEvent.setup();
    
    renderWithQueryClient(
      <CreateLinkForm onSubmit={mockOnSubmit} isLoading={false} />
    );

    const urlInput = screen.getByLabelText(/original url/i);
    const customCodeInput = screen.getByLabelText(/custom short code/i);
    const descriptionInput = screen.getByLabelText(/description/i);
    const submitButton = screen.getByRole('button', { name: /create short link/i });

    await user.type(urlInput, 'https://example.com');
    await user.type(customCodeInput, 'my-link');
    await user.type(descriptionInput, 'Test description');
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        original_url: 'https://example.com',
        custom_short_code: 'my-link',
        description: 'Test description',
      });
    });
  });

  test('does not submit form with empty URL', async () => {
    const user = userEvent.setup();
    
    renderWithQueryClient(
      <CreateLinkForm onSubmit={mockOnSubmit} isLoading={false} />
    );

    const submitButton = screen.getByRole('button', { name: /create short link/i });
    
    await user.click(submitButton);

    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  test('shows loading state when isLoading is true', () => {
    renderWithQueryClient(
      <CreateLinkForm onSubmit={mockOnSubmit} isLoading={true} />
    );

    expect(screen.getByText(/creating.../i)).toBeInTheDocument();
    expect(screen.getByRole('button')).toBeDisabled();
  });

  test('validates URL input', async () => {
    const user = userEvent.setup();
    
    renderWithQueryClient(
      <CreateLinkForm onSubmit={mockOnSubmit} isLoading={false} />
    );

    const urlInput = screen.getByLabelText(/original url/i) as HTMLInputElement;
    
    // Start with empty input
    expect(urlInput.value).toBe('');
    
    // Type a valid URL
    await user.type(urlInput, 'https://example.com');
    
    // Verify the input has the value
    expect(urlInput.value).toBe('https://example.com');
  });
});
