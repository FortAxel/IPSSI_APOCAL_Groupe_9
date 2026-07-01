import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import ResetPasswordPage from './ResetPasswordPage';
import { confirmPasswordReset } from '@/api/auth';

vi.mock('@/api/auth', () => ({
  confirmPasswordReset: vi.fn(),
}));

function renderPage(uid = 'abc', token = 'def') {
  return render(
    <MemoryRouter initialEntries={[`/reset-password/${uid}/${token}`]}>
      <Routes>
        <Route path="/reset-password/:uid/:token" element={<ResetPasswordPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe('ResetPasswordPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('envoie le nouveau mot de passe et affiche un message de succès', async () => {
    vi.mocked(confirmPasswordReset).mockResolvedValue('Mot de passe réinitialisé avec succès.');

    renderPage();

    fireEvent.change(screen.getByLabelText(/nouveau mot de passe/i), {
      target: { value: 'newpassword123' },
    });
    fireEvent.change(screen.getByLabelText(/confirmation du mot de passe/i), {
      target: { value: 'newpassword123' },
    });
    fireEvent.click(screen.getByRole('button', { name: /réinitialiser le mot de passe/i }));

    await waitFor(() => {
      expect(confirmPasswordReset).toHaveBeenCalledWith('abc', 'def', 'newpassword123');
    });

    expect(await screen.findByText(/mot de passe réinitialisé avec succès/i)).toBeInTheDocument();
  });
});
