import { useState, useEffect, type FormEvent } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { generateQuiz, type QuizDifficulty } from '@/api/llm';
import { generateQuizFromCourse } from '@/api/quizzes';
import { listCourses } from '@/api/courses';
import { getApiErrorMessage } from '@/api/errors';

type DifficultyUI = 'facile' | 'moyen' | 'difficile';

const DIFFICULTY_LABELS: Record<DifficultyUI, string> = {
  facile: '🟢 Facile',
  moyen: '🟡 Moyen',
  difficile: '🔴 Difficile',
};

const DIFFICULTY_API: Record<DifficultyUI, QuizDifficulty> = {
  facile: 'easy',
  moyen: 'medium',
  difficile: 'hard',
};

export default function UploadPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const courseIdParam = searchParams.get('course');
  const courseId = courseIdParam ? Number(courseIdParam) : null;
  const fromLibrary = courseId != null && !Number.isNaN(courseId);

  const [title, setTitle] = useState('');
  const [courseTitle, setCourseTitle] = useState<string | null>(null);
  const [mode, setMode] = useState<'pdf' | 'text'>('text');
  const [pdf, setPdf] = useState<File | null>(null);
  const [sourceText, setSourceText] = useState('');
  const [difficulty, setDifficulty] = useState<DifficultyUI>('moyen');
  const [nbQuestions, setNbQuestions] = useState(10);
  const [loading, setLoading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    if (!fromLibrary) return;
    listCourses()
      .then((res) => {
        const course = res.results.find((c) => c.id === courseId);
        if (course) {
          setCourseTitle(course.title);
          setTitle(course.title);
        } else {
          setError('Cours introuvable dans votre bibliothèque.');
        }
      })
      .catch((err) => setError(getApiErrorMessage(err, 'Impossible de charger le cours.')));
  }, [fromLibrary, courseId]);

  useEffect(() => {
    if (!loading) return;
    setElapsed(0);
    const id = setInterval(() => setElapsed((prev) => prev + 1), 1000);
    return () => clearInterval(id);
  }, [loading]);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave' && !e.currentTarget.contains(e.relatedTarget as Node)) {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    const file = e.dataTransfer.files?.[0];
    if (!file) return;
    if (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
      setError('Seuls les fichiers PDF sont acceptés.');
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      setError('Le fichier est trop volumineux (max 5 Mo).');
      return;
    }
    setPdf(file);
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!fromLibrary) {
      if (mode === 'pdf' && !pdf) {
        setError('Veuillez sélectionner un fichier PDF.');
        return;
      }
    }

    const apiDifficulty = DIFFICULTY_API[difficulty];
    setLoading(true);
    try {
      const quiz = fromLibrary
        ? await generateQuizFromCourse({
            course_id: courseId!,
            difficulty: apiDifficulty,
            nb_questions: nbQuestions,
          })
        : await generateQuiz({
            title,
            pdf: mode === 'pdf' ? (pdf ?? undefined) : undefined,
            source_text: mode === 'text' ? sourceText : undefined,
            difficulty: apiDifficulty,
            nb_questions: nbQuestions,
          });
      navigate(`/quiz/${quiz.id}`);
    } catch (err) {
      setError(getApiErrorMessage(err, 'Échec de la génération.'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold text-slate-900 mb-2">Créer un quiz</h1>
      <p className="text-slate-600 mb-6">
        {fromLibrary && courseTitle
          ? `Génération depuis votre bibliothèque : « ${courseTitle} ».`
          : 'Uploadez un PDF ou collez un texte, choisissez la difficulté et le nombre de questions.'}
      </p>

      {error && (
        <div className="mb-4 p-3 bg-rose-50 border-l-4 border-rose-500 text-sm text-rose-900 rounded">
          <p>{error}</p>
          {!loading && (
            <button
              type="button"
              onClick={() => setError(null)}
              className="mt-1 text-xs font-semibold text-rose-700 hover:text-rose-900 underline"
            >
              Réessayer
            </button>
          )}
        </div>
      )}

      <form onSubmit={handleSubmit} className="card space-y-4">
        {!fromLibrary && (
          <>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Titre du cours
              </label>
              <input
                type="text"
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Ex. Histoire — Révolution française"
                className="input"
              />
            </div>

            <div>
              <div className="flex gap-2 mb-3">
                <button
                  type="button"
                  onClick={() => setMode('text')}
                  className={`px-3 py-1 rounded text-sm font-medium ${
                    mode === 'text'
                      ? 'bg-indigo-600 text-white'
                      : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                  }`}
                >
                  📝 Texte collé
                </button>
                <button
                  type="button"
                  onClick={() => setMode('pdf')}
                  className={`px-3 py-1 rounded text-sm font-medium ${
                    mode === 'pdf'
                      ? 'bg-indigo-600 text-white'
                      : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                  }`}
                >
                  📄 PDF
                </button>
              </div>

              {mode === 'text' ? (
                <textarea
                  required
                  rows={10}
                  minLength={200}
                  value={sourceText}
                  onChange={(e) => setSourceText(e.target.value)}
                  placeholder="Collez ici le texte de votre cours (au moins 200 caractères)…"
                  className="input"
                />
              ) : (
                <div
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                  className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                    dragActive
                      ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-950'
                      : pdf
                        ? 'border-emerald-500 bg-emerald-50 dark:bg-emerald-950'
                        : 'border-slate-300 dark:border-slate-600'
                  }`}
                >
                  <input
                    type="file"
                    accept=".pdf,application/pdf"
                    onChange={(e) => {
                      const file = e.target.files?.[0] ?? null;
                      if (file && file.size > 5 * 1024 * 1024) {
                        setError('Le fichier est trop volumineux (max 5 Mo).');
                        setPdf(null);
                        return;
                      }
                      setPdf(file);
                    }}
                    className="hidden"
                    id="pdf-upload"
                  />
                  {pdf ? (
                    <div className="flex flex-col items-center gap-2">
                      <span className="text-2xl">📄</span>
                      <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                        {pdf.name}
                      </span>
                      <button
                        type="button"
                        onClick={() => setPdf(null)}
                        className="text-xs text-rose-600 hover:text-rose-800 dark:text-rose-400 dark:hover:text-rose-300 font-medium"
                      >
                        ✕ Retirer
                      </button>
                    </div>
                  ) : (
                    <label
                      htmlFor="pdf-upload"
                      className="cursor-pointer flex flex-col items-center gap-2"
                    >
                      <span className="text-2xl">📤</span>
                      <span className="text-sm font-medium text-slate-600 dark:text-slate-400">
                        Glissez-déposez un PDF ici ou{' '}
                        <span className="text-indigo-600 dark:text-indigo-400 underline">
                          cliquez pour parcourir
                        </span>
                      </span>
                      <span className="text-xs text-slate-400 dark:text-slate-500">
                        PDF uniquement
                      </span>
                    </label>
                  )}
                </div>
              )}
              {mode === 'text' && (
                <p className="text-xs text-slate-500 mt-1">
                  {sourceText.length} / 200 caractères minimum
                </p>
              )}
            </div>
          </>
        )}

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Difficulté</label>
          <div className="flex gap-2">
            {(Object.keys(DIFFICULTY_LABELS) as DifficultyUI[]).map((level) => (
              <button
                key={level}
                type="button"
                onClick={() => setDifficulty(level)}
                className={`flex-1 px-3 py-2 rounded text-sm font-medium transition-colors ${
                  difficulty === level
                    ? 'bg-indigo-600 text-white'
                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                }`}
              >
                {DIFFICULTY_LABELS[level]}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Nombre de questions&nbsp;
            <span className="font-mono text-indigo-600">{nbQuestions}</span>
          </label>
          <input
            type="range"
            min={5}
            max={20}
            step={1}
            value={nbQuestions}
            onChange={(e) => setNbQuestions(Number(e.target.value))}
            className="w-full accent-indigo-600"
          />
          <div className="flex justify-between text-xs text-slate-400 mt-1">
            <span>5</span>
            <span>20</span>
          </div>
        </div>

        <button
          type="submit"
          disabled={loading || (fromLibrary && !courseTitle)}
          className="btn-primary w-full"
        >
          {loading ? (
            <>
              <span className="animate-spin">⏳</span> Génération en cours…
              {elapsed < 60
                ? ` (${elapsed} s)`
                : ` (${Math.floor(elapsed / 60)} min ${elapsed % 60} s)`}
            </>
          ) : (
            <>
              🚀 Générer le quiz ({nbQuestions} QCM — {DIFFICULTY_LABELS[difficulty]})
            </>
          )}
        </button>

        <p className="text-xs text-slate-500 text-center">
          La génération peut prendre de 1 à 5 minutes selon votre machine (bien plus rapide avec un
          GPU ou un modèle plus léger).
        </p>
      </form>
    </div>
  );
}
