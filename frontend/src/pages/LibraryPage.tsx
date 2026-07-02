import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { listCourses, type CourseSummary } from '@/api/courses';
import { getApiErrorMessage } from '@/api/errors';

export default function LibraryPage() {
  const [courses, setCourses] = useState<CourseSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listCourses()
      .then((res) => setCourses(res.results))
      .catch((err) => setError(getApiErrorMessage(err, 'Impossible de charger la bibliothèque.')))
      .finally(() => setLoading(false));
  }, []);

  if (loading)
    return (
      <div className="text-center py-12">
        <span className="animate-spin inline-block text-2xl">⏳</span>
        <p className="text-slate-500 mt-3">Chargement de la bibliothèque…</p>
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
          <h1 className="text-3xl font-bold text-slate-900">Ma bibliothèque</h1>
          <p className="text-slate-500 text-sm">
            {courses.length === 0
              ? "Aucun cours pour l'instant — importez votre premier !"
              : `${courses.length} cours importé${courses.length > 1 ? 's' : ''}.`}
          </p>
        </div>
        <Link to="/upload" className="btn-primary">
          + Importer un cours
        </Link>
      </div>

      {courses.length === 0 ? (
        <div className="card text-center py-12">
          <div className="text-5xl mb-4">📖</div>
          <p className="text-slate-600 mb-2 font-medium">Votre bibliothèque est vide.</p>
          <p className="text-slate-500 text-sm mb-6">
            Importez un cours PDF ou collez du texte pour générer votre premier quiz.
          </p>
          <Link to="/upload" className="btn-primary">
            Importer mon premier cours
          </Link>
        </div>
      ) : (
        <div className="grid sm:grid-cols-2 gap-4">
          {courses.map((course) => (
            <div key={course.id} className="card flex flex-col">
              <div className="flex items-center justify-between mb-2">
                <span className="font-mono text-xs text-slate-500">
                  {new Date(course.created_at).toLocaleDateString('fr-FR')}
                </span>
                <span className="px-2 py-0.5 rounded bg-indigo-100 text-indigo-700 text-xs font-mono">
                  {course.nb_quizz} quiz
                </span>
              </div>
              <h3 className="font-semibold text-slate-900 mb-4">{course.title}</h3>
              <div className="mt-auto flex justify-end">
                <Link to={`/quiz?course=${course.id}`} className="btn-primary text-sm">
                  Générer un quiz
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
