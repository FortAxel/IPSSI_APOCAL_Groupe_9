import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import QuizPage from './QuizPage';
import { getQuiz, submitAnswers } from '@/api/quizzes';

vi.mock('@/api/quizzes', () => ({
  getQuiz: vi.fn(),
  submitAnswers: vi.fn(),
}));

function renderPage() {
  return render(
    <MemoryRouter initialEntries={['/quiz/42']}>
      <Routes>
        <Route path="/quiz/:id" element={<QuizPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe('QuizPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    window.scrollTo = vi.fn();
  });

  it('charge le quiz, soumet les réponses et affiche la correction', async () => {
    vi.mocked(getQuiz).mockResolvedValue({
      id: 42,
      title: 'Quiz de test',
      source_text: 'Texte du cours',
      score: null,
      created_at: '2026-06-30T10:00:00Z',
      questions: Array.from({ length: 10 }, (_, index) => ({
        index: index + 1,
        prompt: `Question ${index + 1} ?`,
        options: ['Option A', 'Option B', 'Option C', 'Option D'],
        correct_index: 0,
      })),
    });

    vi.mocked(submitAnswers).mockResolvedValue({
      score: 8,
      total: 10,
      details: Array.from({ length: 10 }, (_, index) => ({
        index: index + 1,
        selected_index: 0,
        correct_index: 0,
        correct: true,
      })),
    });

    const { container } = renderPage();

    await waitFor(() => {
      expect(getQuiz).toHaveBeenCalledWith(42);
    });

    expect(await screen.findByText('Quiz de test')).toBeInTheDocument();

    const optionButtons = screen.getAllByRole('button', { name: /^A\. / });
    expect(optionButtons).toHaveLength(10);
    optionButtons.forEach((button) => fireEvent.click(button));

    const submitButton = screen.getByRole('button', { name: /soumettre mes réponses/i });
    expect(submitButton).not.toBeDisabled();

    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(submitAnswers).toHaveBeenCalledWith(
        42,
        Array.from({ length: 10 }, (_, index) => ({
          index: index + 1,
          selected_index: 0,
        })),
      );
    });

    expect(await screen.findByText(/Score : 8 \/ 10/)).toBeInTheDocument();
  });
});
