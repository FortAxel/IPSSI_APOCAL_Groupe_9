import { api } from './client';

export type CourseSummary = {
  id: number;
  title: string;
  nb_quizz: number;
  created_at: string;
};

type PaginatedCourses = {
  count: number;
  next: string | null;
  previous: string | null;
  results: CourseSummary[];
};

export async function listCourses(): Promise<PaginatedCourses> {
  const { data } = await api.get<PaginatedCourses>('/courses/');
  return data;
}
