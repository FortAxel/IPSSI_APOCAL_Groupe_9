import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getQuiz, submitAnswers, type Quiz, type AnswerResult } from '@/api/quizzes';
import { getApiErrorMessage } from '@/api/errors';

export default function QuizPage() {
  const { id } = useParams<{ id: string }>();
  const quizId = Number(id);

  const [quiz, setQuiz] = useState<Quiz | null>(null);
  const [answers, setAnswers] = useState<Record<number, number>>({});
  const [result, setResult] = useState<AnswerResult | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isNaN(quizId)) {
      setError('Quiz introuvable.');
      setLoading(false);
      return;
    }
    setLoading(true);
    getQuiz(quizId)
      .then(setQuiz)
      .catch((err) => setError(getApiErrorMessage(err, 'Impossible de charger ce quiz.')))
      .finally(() => setLoading(false));
  }, [quizId]);

  const handleSelect = (questionIndex: number, optionIndex: number) => {
    if (result) return; // déjà soumis
    setAnswers((prev) => ({ ...prev, [questionIndex]: optionIndex }));
  };

  const handleSubmit = async () => {
    if (!quiz || Object.keys(answers).length !== quiz.questions.length) return;
    setSubmitting(true);
    try {
      const payload = quiz.questions.map((q) => ({
        index: q.index,
        selected_index: answers[q.index]!,
      }));
      const res = await submitAnswers(quiz.id, payload);
      setResult(res);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      setError(getApiErrorMessage(err, 'Échec de la soumission.'));
    } finally {
      setSubmitting(false);
    }
  };

  if (loading)
    return (
      <div className="max-w-3xl mx-auto text-center py-12">
        <span className="animate-spin inline-block text-2xl">⏳</span>
        <p className="text-slate-500 mt-3">Chargement du quiz…</p>
      </div>
    );
  if (!quiz) {
    return (
      <div className="max-w-3xl mx-auto">
        <div className="p-3 bg-rose-50 border-l-4 border-rose-500 text-sm text-rose-900 rounded">
          {error ?? 'Quiz introuvable.'}
        </div>
      </div>
    );
  }

  const allAnswered = Object.keys(answers).length === quiz.questions.length;

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {error && (
        <div className="p-3 bg-rose-50 border-l-4 border-rose-500 text-sm text-rose-900 rounded">
          <p>{error}</p>
        </div>
      )}
      {/* En-tête */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">{quiz.title}</h1>
        <p className="text-sm text-slate-500">
          Quiz #{quiz.id} · {quiz.questions.length} questions
        </p>
      </div>

      {/* Résultat */}
      {result && (
        <div
          className={`card border-l-4 ${
            result.score >= 7
              ? 'border-emerald-500 bg-emerald-50'
              : result.score >= 4
                ? 'border-amber-500 bg-amber-50'
                : 'border-rose-500 bg-rose-50'
          }`}
        >
          <h2 className="text-3xl font-bold text-slate-900 mb-1">
            Score : {result.score} / {result.total}
            <span className="text-lg font-normal text-slate-500 ml-2">
              ({Math.round((result.score / result.total) * 100)}%)
            </span>
          </h2>
          <div className="w-full bg-slate-200 rounded-full h-2.5 mb-3">
            <div
              className={`h-2.5 rounded-full transition-all duration-700 ${
                result.score >= 7
                  ? 'bg-emerald-500'
                  : result.score >= 4
                    ? 'bg-amber-500'
                    : 'bg-rose-500'
              }`}
              style={{ width: `${(result.score / result.total) * 100}%` }}
            />
          </div>
          <p className="text-slate-700">
            {result.score === 10
              ? '🎉 Sans-faute ! Tu maitrises ce chapitre.'
              : result.score >= 7
                ? '👍 Bon résultat. Revois les questions ratées en bas de page.'
                : result.score >= 4
                  ? "📚 Tu as les bases, mais des révisions s'imposent."
                  : '⚠️ Il faut reprendre le cours en profondeur.'}
          </p>
          <div className="flex flex-wrap gap-3 mt-4">
            <button
              type="button"
              onClick={() => {
                setAnswers({});
                setResult(null);
                setError(null);
                window.scrollTo({ top: 0, behavior: 'smooth' });
              }}
              className="btn-primary"
            >
              🔄 Refaire ce quiz
            </button>
            <Link to="/history" className="btn-secondary inline-flex">
              Retour à l'historique
            </Link>
          </div>
        </div>
      )}

      {/* Questions */}
      {quiz.questions?.map((q) => {
        const userChoice = answers[q.index];
        const detail = result?.details.find((d) => d.index === q.index);

        return (
          <article key={q.index} className="card">
            <div className="flex items-baseline gap-2 mb-3">
              <span className="font-mono text-sm text-indigo-600">Q{q.index}</span>
              <h3 className="font-semibold text-slate-900">{q.prompt}</h3>
            </div>
            <div className="space-y-2">
              {q.options?.map((opt, optIdx) => {
                const isSelected = userChoice === optIdx;
                const isCorrect = detail && q.correct_index === optIdx;
                const isWrongPick = detail && isSelected && !detail.correct;

                let cls = 'border-slate-200 hover:bg-slate-50';
                if (result) {
                  if (isCorrect) cls = 'border-emerald-500 bg-emerald-50';
                  else if (isWrongPick) cls = 'border-rose-500 bg-rose-50';
                  else cls = 'border-slate-200 opacity-60';
                } else if (isSelected) {
                  cls = 'border-indigo-500 bg-indigo-50';
                }

                return (
                  <button
                    key={optIdx}
                    type="button"
                    disabled={!!result}
                    onClick={() => handleSelect(q.index, optIdx)}
                    className={`w-full text-left p-3 border-2 rounded transition ${cls}`}
                  >
                    <span className="font-mono mr-2 text-slate-500">
                      {String.fromCharCode(65 + optIdx)}.
                    </span>
                    {opt}
                    {result && isCorrect && (
                      <span className="ml-2 text-emerald-600 font-bold">✓</span>
                    )}
                    {result && isWrongPick && (
                      <span className="ml-2 text-rose-600 font-bold">✗</span>
                    )}
                  </button>
                );
              })}
            </div>
          </article>
        );
      })}

      {/* Soumission */}
      {!result && (
        <button
          onClick={handleSubmit}
          disabled={!allAnswered || submitting}
          className="btn-signature w-full py-3 text-base"
        >
          {submitting
            ? 'Correction en cours…'
            : allAnswered
              ? '🎯 Soumettre mes réponses'
              : `Répondre à toutes les questions (${Object.keys(answers).length}/${quiz.questions.length})`}
        </button>
      )}
    </div>
  );
}
