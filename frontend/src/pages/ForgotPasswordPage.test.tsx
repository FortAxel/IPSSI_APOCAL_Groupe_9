import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import ForgotPasswordPage from './ForgotPasswordPage';
import { requestPasswordReset } from '@/api/auth';

vi.mock('@/api/auth', () => ({
  requestPasswordReset: vi.fn(),
}));

vi.mock('@/api/errors', () => ({
  getApiErrorMessage: () => 'Impossible d’envoyer le lien.',
}));

function renderPage() {
  return render(
    <MemoryRouter>
      <ForgotPasswordPage />
    </MemoryRouter>,
  );
}

describe('ForgotPasswordPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('envoie le lien de reset et affiche le message de confirmation', async () => {
    vi.mocked(requestPasswordReset).mockResolvedValue(
      "Si un compte existe pour cet email, un lien de réinitialisation vient d'être envoyé.",
    );

    renderPage();

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'alice@test.com' },
    });
    fireEvent.click(screen.getByRole('button', { name: /envoyer le lien/i }));

    await waitFor(() => {
      expect(requestPasswordReset).toHaveBeenCalledWith('alice@test.com');
    });

    expect(await screen.findByText(/si un compte existe pour cet email/i)).toBeInTheDocument();
  });
});
