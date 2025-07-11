import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from './App';

// Mock fetch for API calls
global.fetch = jest.fn();

describe('LinkDisplay App', () => {
  beforeEach(() => {
    fetch.mockClear();
    
    // Default mock responses
    fetch.mockResolvedValue({
      ok: true,
      json: async () => ({
        success: true,
        data: []
      })
    });
  });

  test('renders app title and tagline after loading', async () => {
    render(<App />);
    
    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
    });
    
    expect(screen.getByText('Your links, organized.')).toBeInTheDocument();
    expect(screen.getByText('a product of perspective computing')).toBeInTheDocument();
  });

  test('shows add link button by default after loading', async () => {
    render(<App />);
    
    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
    });
    
    expect(screen.getByText('Add Link')).toBeInTheDocument();
  });

  test('shows add category button by default after loading', async () => {
    render(<App />);
    
    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
    });
    
    expect(screen.getByText('＋')).toBeInTheDocument();
  });

  test('handles API errors gracefully', async () => {
    fetch.mockRejectedValueOnce(new Error('Network error'));
    
    render(<App />);
    
    // Wait for error message to appear
    const errorMessage = await screen.findByText(/Failed to load data/);
    expect(errorMessage).toBeInTheDocument();
  });

  test('loads and displays categories when API call succeeds', async () => {
    // Mock categories data
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success: true,
        data: [{ id: 1, name: 'Work' }]
      })
    });

    render(<App />);
    
    // Wait for category to appear
    const categoryElement = await screen.findByText('Work');
    expect(categoryElement).toBeInTheDocument();
  });

  test('loads and displays links when API call succeeds', async () => {
    // Mock both categories and links data (app makes two API calls)
    fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          data: [{ id: 1, name: 'Work' }]
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          data: [{ id: 1, title: 'Test Link', url: 'https://example.com', categoryId: 1 }]
        })
      });

    render(<App />);
    
    // Wait for link to appear
    const linkElement = await screen.findByText('Test Link');
    expect(linkElement).toBeInTheDocument();
  });
});
