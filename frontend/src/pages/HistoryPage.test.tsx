import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import HistoryPage from './HistoryPage';
import { listQuizzes } from '@/api/quizzes';

vi.mock('@/api/quizzes', () => ({
  listQuizzes: vi.fn(),
}));

function renderPage() {
  return render(
    <MemoryRouter>
      <HistoryPage />
    </MemoryRouter>,
  );
}

describe('HistoryPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('affiche les quiz de l historique', async () => {
    vi.mocked(listQuizzes).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [
        {
          id: 99,
          title: 'Quiz React',
          score: 8,
          nb_questions: 10,
          created_at: '2026-06-30T10:00:00Z',
        },
      ],
    });

    renderPage();

    expect(await screen.findByText('Mon historique')).toBeInTheDocument();
    expect(await screen.findByText('Quiz React')).toBeInTheDocument();
    expect(screen.getByText(/8 \/ 10/)).toBeInTheDocument();
  });
});
