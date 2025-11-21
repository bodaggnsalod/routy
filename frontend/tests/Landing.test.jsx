import { render, screen, waitFor } from '@testing-library/react';
import Landing from '../src/components/Landing';
import { vi } from 'vitest';

describe('Landing', () => {
  beforeEach(() => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ status: 'ok' })
    });
  });

  it('shows logo and api status', async () => {
    render(<Landing />);
    expect(screen.getByAltText('logo')).toBeInTheDocument();
    await waitFor(() => expect(screen.getByText(/API:/)).toBeInTheDocument());
    expect(screen.getByText(/API: ok/i)).toBeInTheDocument();
  });
});