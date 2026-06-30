import { useState } from 'react';
import { Link } from 'react-router-dom';
import { generateQuiz } from '@/api/llm';
import { getApiErrorMessage } from '@/api/errors';
import type { Quiz } from '@/api/quizzes';

type Phase = 'form' | 'loading' | 'result';

export default function GenerateQuizPage() {
  const [title, setTitle] = useState('');
  const [sourceText, setSourceText] = useState('');
  const [phase, setPhase] = useState<Phase>('form');
  const [quiz, setQuiz] = useState<Quiz | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    setError(null);
    setPhase('loading');
    try {
      const generated = await generateQuiz({ title, source_text: sourceText });
      setQuiz(generated);
      setPhase('result');
    } catch (err) {
      setError(getApiErrorMessage(err, 'Échec de la génération.'));
      setPhase('form');
    }
  };

  const handleReset = () => {
    setPhase('form');
    setQuiz(null);
    setTitle('');
    setSourceText('');
    setError(null);
  };

  if (phase === 'loading') {
    return (
      <div className="max-w-2xl mx-auto text-center py-20">
        <div className="text-5xl mb-6 inline-block animate-spin">⏳</div>
        <h2 className="text-xl font-semibold text-slate-700 mb-2">Génération en cours…</h2>
        <p className="text-slate-500 text-sm">
          Le LLM génère 10 QCM à partir de votre cours.
          <br />
          Cela peut prendre jusqu'à 5 minutes sur CPU.
        </p>
      </div>
    );
  }

  if (phase === 'result' && quiz) {
    return (
      <div className="max-w-3xl mx-auto space-y-6">
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">{quiz.title}</h1>
            <p className="text-sm text-slate-500">{quiz.questions.length} questions générées</p>
          </div>
          <div className="flex gap-3">
            <button onClick={handleReset} className="btn-secondary">
              Nouveau quiz
            </button>
            <Link to={`/quiz/${quiz.id}`} className="btn-signature">
              Répondre au quiz
            </Link>
          </div>
        </div>

        {quiz.questions.map((q) => (
          <article key={q.index} className="card">
            <div className="flex items-baseline gap-2 mb-3">
              <span className="font-mono text-sm text-indigo-600">Q{q.index}</span>
              <h3 className="font-semibold text-slate-900">{q.prompt}</h3>
            </div>
            <ul className="space-y-1.5">
              {q.options.map((opt, i) => (
                <li
                  key={i}
                  className="flex items-center gap-2 text-sm text-slate-700 p-2 rounded border border-slate-200"
                >
                  <span className="font-mono text-slate-400 shrink-0">
                    {String.fromCharCode(65 + i)}.
                  </span>
                  {opt}
                </li>
              ))}
            </ul>
          </article>
        ))}

        <Link
          to={`/quiz/${quiz.id}`}
          className="btn-signature w-full text-center block py-3 text-base"
        >
          Répondre au quiz
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold text-slate-900 mb-2">Générer un quiz</h1>
      <p className="text-slate-600 mb-6">
        Collez le texte de votre cours. EduTutor IA génère 10 questions QCM.
      </p>

      {error && (
        <div className="mb-4 p-3 bg-rose-50 border-l-4 border-rose-500 text-sm text-rose-900 rounded">
          {error}
        </div>
      )}

      <div className="card space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Titre du cours</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Ex. Histoire — Révolution française"
            className="input"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Contenu du cours
          </label>
          <textarea
            rows={10}
            value={sourceText}
            onChange={(e) => setSourceText(e.target.value)}
            placeholder="Collez ici le texte de votre cours (au moins 200 caractères)…"
            className="input"
          />
          <p className="text-xs text-slate-500 mt-1">
            {sourceText.length} / 200 caractères minimum
          </p>
        </div>

        <button
          onClick={handleGenerate}
          disabled={!title.trim() || sourceText.length < 200}
          className="btn-primary w-full py-3 text-base"
        >
          Générer un quiz
        </button>
      </div>
    </div>
  );
}
