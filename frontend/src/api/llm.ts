import { api } from './client';
import type { Quiz } from './quizzes';

export type LLMPing = {
  backend: 'ollama' | 'mock';
  model: string;
  ollama_alive: boolean;
  model_loaded?: boolean;
  message: string;
};

export async function ping(): Promise<LLMPing> {
  const { data } = await api.get<LLMPing>('/llm/ping/');
  return data;
}

/**
 * Génère un quiz à partir d'un PDF ou d'un texte.
 * Renvoie le quiz complet (avec les 10 questions et leur bonne réponse).
 */
export type QuizDifficulty = 'easy' | 'medium' | 'hard';

export async function generateQuiz(input: {
  title: string;
  pdf?: File;
  source_text?: string;
  difficulty?: QuizDifficulty;
  nb_questions?: number;
}): Promise<Quiz> {
  const form = new FormData();
  form.append('title', input.title);
  if (input.pdf) form.append('pdf', input.pdf);
  if (input.source_text) form.append('source_text', input.source_text);
  if (input.difficulty) form.append('difficulty', input.difficulty);
  if (input.nb_questions != null) form.append('nb_questions', String(input.nb_questions));

  const { data } = await api.post<Quiz>('/llm/generate-quiz/', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    // La génération LLM sur CPU peut prendre plusieurs minutes : on dépasse
    // largement le timeout axios par défaut (120 s). Aligné sur OLLAMA_TIMEOUT.
    timeout: 600_000,
  });
  return data;
}
