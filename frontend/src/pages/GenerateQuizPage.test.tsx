import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import GenerateQuizPage from './GenerateQuizPage';
import { generateQuiz } from '@/api/llm';

vi.mock('@/api/llm', () => ({
  generateQuiz: vi.fn(),
}));

describe('GenerateQuizPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('génère et affiche un quiz quand le formulaire est valide', async () => {
    vi.mocked(generateQuiz).mockResolvedValue({
      id: 7,
      title: 'Cours React',
      source_text: 'Contenu très long',
      score: null,
      created_at: '2026-06-30T10:00:00Z',
      questions: [
        {
          index: 1,
          prompt: 'Quelle est la bonne réponse ?',
          options: ['Oui', 'Non', 'Peut-être', 'Jamais'],
          correct_index: 0,
        },
      ],
    });

    render(
      <MemoryRouter>
        <GenerateQuizPage />
      </MemoryRouter>,
    );

    fireEvent.change(screen.getByPlaceholderText(/Ex\. Histoire — Révolution française/i), {
      target: { value: 'Cours React' },
    });
    fireEvent.change(screen.getByPlaceholderText(/Collez ici le texte de votre cours/i), {
      target: { value: 'Contenu du cours '.repeat(20) },
    });
    fireEvent.click(screen.getByRole('button', { name: /Générer un quiz/i }));

    await waitFor(() => {
      expect(generateQuiz).toHaveBeenCalled();
    });
    expect(await screen.findByText('Cours React')).toBeInTheDocument();
    expect(screen.getByText(/1 questions générées/i)).toBeInTheDocument();
  });
});
