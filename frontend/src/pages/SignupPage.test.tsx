import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import SignupPage from './SignupPage';
import { signup } from '@/api/auth';

const navigateMock = vi.hoisted(() => vi.fn());
const refreshMock = vi.hoisted(() => vi.fn());

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom');
  return {
    ...actual,
    useNavigate: () => navigateMock,
  };
});

vi.mock('@/api/auth', () => ({
  signup: vi.fn(),
}));

vi.mock('@/api/errors', () => ({
  getApiErrorMessage: () => 'Cet email est deja utilise.',
}));

vi.mock('@/contexts/AuthContext', () => ({
  useAuth: () => ({
    refresh: refreshMock,
  }),
}));

vi.mock('@/contexts/SiteConfigContext', () => ({
  useSiteConfig: () => ({
    config: {
      app_name: 'EduTutor IA',
      allow_signups: true,
      banner_enabled: false,
      banner_message: '',
    },
  }),
}));

function renderPage() {
  return render(
    <MemoryRouter>
      <SignupPage />
    </MemoryRouter>,
  );
}

describe('SignupPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('envoie les champs du formulaire puis redirige vers upload', async () => {
    vi.mocked(signup).mockResolvedValue({
      id: 1,
      username: 'ryma@test.com',
      email: 'ryma@test.com',
    });

    const { container } = renderPage();

    fireEvent.change(container.querySelector('input[type="email"]')!, {
      target: { value: 'ryma@test.com' },
    });
    fireEvent.change(container.querySelector('input[autocomplete="given-name"]')!, {
      target: { value: 'Ryma' },
    });
    fireEvent.change(container.querySelector('input[autocomplete="family-name"]')!, {
      target: { value: 'Test' },
    });
    fireEvent.change(container.querySelector('input[type="password"]')!, {
      target: { value: 'motdepasse123' },
    });
    fireEvent.click(container.querySelector('button[type="submit"]')!);

    await waitFor(() => {
      expect(signup).toHaveBeenCalledWith({
        email: 'ryma@test.com',
        password: 'motdepasse123',
        first_name: 'Ryma',
        last_name: 'Test',
      });
    });
    expect(refreshMock).toHaveBeenCalledTimes(1);
    expect(navigateMock).toHaveBeenCalledWith('/upload', { replace: true });
  });

  it("affiche le message d'erreur quand l'inscription echoue", async () => {
    vi.mocked(signup).mockRejectedValue({
      response: { data: { email: ['Cet email est deja utilise.'] } },
    });

    const { container } = renderPage();

    fireEvent.change(container.querySelector('input[type="email"]')!, {
      target: { value: 'ryma@test.com' },
    });
    fireEvent.change(container.querySelector('input[type="password"]')!, {
      target: { value: 'motdepasse123' },
    });
    fireEvent.click(container.querySelector('button[type="submit"]')!);

    expect(await screen.findByText(/cet email est deja utilise/i)).toBeInTheDocument();
    expect(navigateMock).not.toHaveBeenCalled();
  });
});
