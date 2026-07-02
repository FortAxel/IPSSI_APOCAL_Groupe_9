import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import UploadPage from './UploadPage';
import { generateQuiz } from '@/api/llm';

const navigateMock = vi.hoisted(() => vi.fn());

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom');
  return {
    ...actual,
    useNavigate: () => navigateMock,
  };
});

vi.mock('@/api/llm', () => ({
  generateQuiz: vi.fn(),
}));

vi.mock('@/api/errors', () => ({
  getApiErrorMessage: () => 'Echec de la generation.',
}));

function renderPage() {
  return render(
    <MemoryRouter>
      <UploadPage />
    </MemoryRouter>,
  );
}

describe('UploadPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('envoie un texte de cours et redirige vers le quiz cree', async () => {
    vi.mocked(generateQuiz).mockResolvedValue({
      id: 42,
      title: 'Cours React',
      source_text: 'Contenu du cours. '.repeat(20),
      score: null,
      created_at: '2026-06-30T10:00:00Z',
      questions: [],
    });

    const { container } = renderPage();

    fireEvent.change(container.querySelector('input[type="text"]')!, {
      target: { value: 'Cours React' },
    });
    fireEvent.change(container.querySelector('textarea')!, {
      target: { value: 'Contenu du cours. '.repeat(20) },
    });
    fireEvent.click(container.querySelector('button[type="submit"]')!);

    await waitFor(() => {
      expect(generateQuiz).toHaveBeenCalledWith({
        title: 'Cours React',
        pdf: undefined,
        source_text: 'Contenu du cours. '.repeat(20),
        difficulty: 'medium',
        nb_questions: 10,
      });
    });
    expect(navigateMock).toHaveBeenCalledWith('/quiz/42');
  });

  it('bascule en mode PDF et envoie le fichier choisi', async () => {
    vi.mocked(generateQuiz).mockResolvedValue({
      id: 7,
      title: 'Cours PDF',
      source_text: 'Texte extrait',
      score: null,
      created_at: '2026-06-30T10:00:00Z',
      questions: [],
    });

    const { container } = renderPage();
    const file = new File(['pdf'], 'cours.pdf', { type: 'application/pdf' });

    fireEvent.change(container.querySelector('input[type="text"]')!, {
      target: { value: 'Cours PDF' },
    });
    fireEvent.click(screen.getByRole('button', { name: /pdf/i }));
    fireEvent.change(container.querySelector('input[type="file"]')!, {
      target: { files: [file] },
    });
    fireEvent.submit(container.querySelector('form')!);

    await waitFor(() => {
      expect(generateQuiz).toHaveBeenCalledWith({
        title: 'Cours PDF',
        pdf: file,
        source_text: undefined,
        difficulty: 'medium',
        nb_questions: 10,
      });
    });
    expect(navigateMock).toHaveBeenCalledWith('/quiz/7');
  });

  it("affiche une erreur quand l'upload echoue", async () => {
    vi.mocked(generateQuiz).mockRejectedValue(new Error('bad upload'));

    const { container } = renderPage();

    fireEvent.change(container.querySelector('input[type="text"]')!, {
      target: { value: 'Cours invalide' },
    });
    fireEvent.change(container.querySelector('textarea')!, {
      target: { value: 'Texte valide pour declencher l appel API. '.repeat(10) },
    });
    fireEvent.click(container.querySelector('button[type="submit"]')!);

    expect(await screen.findByText(/echec de la generation/i)).toBeInTheDocument();
    expect(navigateMock).not.toHaveBeenCalled();
  });
});
