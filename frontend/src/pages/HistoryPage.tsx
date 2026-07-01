import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { listQuizzes, type QuizSummary } from '@/api/quizzes';
import { getApiErrorMessage } from '@/api/errors';

export default function HistoryPage() {
  const [quizzes, setQuizzes] = useState<QuizSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listQuizzes()
      .then((res) => setQuizzes(res.results))
      .catch((err) => setError(getApiErrorMessage(err, "Impossible de charger l'historique.")))
      .finally(() => setLoading(false));
  }, []);

  if (loading)
    return (
      <div className="text-center py-12">
        <span className="animate-spin inline-block text-2xl">⏳</span>
        <p className="text-slate-500 mt-3">Chargement de l'historique…</p>
      </div>
    );

  if (error)
    return (
      <div className="max-w-3xl mx-auto">
        <div className="p-3 bg-rose-50 border-l-4 border-rose-500 text-sm text-rose-900 rounded">
          {error}
        </div>
      </div>
    );

  return (
    <div className="space-y-4">
      <div className="flex items-end justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Mon historique</h1>
          <p className="text-slate-500 text-sm">
            {quizzes.length === 0
              ? "Aucun quiz pour l'instant — créez votre premier !"
              : `${quizzes.length} quiz au compteur.`}
          </p>
        </div>
        <Link to="/upload" className="btn-primary">
          + Nouveau quiz
        </Link>
      </div>

      {quizzes.length === 0 ? (
        <div className="card text-center py-12">
          <div className="text-5xl mb-4">📚</div>
          <p className="text-slate-600 mb-4">Pas encore de quiz dans votre historique.</p>
          <Link to="/upload" className="btn-primary">
            Créer mon premier quiz
          </Link>
        </div>
      ) : (
        <div className="grid sm:grid-cols-2 gap-4">
          {quizzes.map((q) => (
            <div key={q.id} className="card flex flex-col">
              <div className="flex items-center justify-between mb-2">
                <span className="font-mono text-xs text-slate-500">
                  #{q.id} · {new Date(q.created_at).toLocaleDateString('fr-FR')}
                </span>
                {q.score !== null ? (
                  <span
                    className={`px-2 py-0.5 rounded font-mono text-sm font-bold ${
                      q.score >= 7
                        ? 'bg-emerald-100 text-emerald-700'
                        : q.score >= 4
                          ? 'bg-amber-100 text-amber-700'
                          : 'bg-rose-100 text-rose-700'
                    }`}
                  >
                    {q.score} / 10
                  </span>
                ) : (
                  <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-600 text-xs font-mono">
                    pas encore passé
                  </span>
                )}
              </div>
              <h3 className="font-semibold text-slate-900 mb-1">{q.title}</h3>
              <p className="text-sm text-slate-500 mb-4">{q.nb_questions} questions</p>
              <div className="mt-auto flex justify-end">
                <Link to={`/quiz/${q.id}`} className="btn-primary text-sm">
                  🔄 Refaire
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
