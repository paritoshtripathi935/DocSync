import { Link } from 'react-router-dom';
import { useNotes } from '../state/NotesContext';
import ErrorNote from '../components/ErrorNote';
import { ago } from '../utils/time';

export default function HomePage() {
  const { notes, loading, error } = useNotes();
  return (
    <div className="mx-auto max-w-3xl px-6 sm:px-10 py-16">
      <h1 className="font-serif text-4xl font-medium">Your notes</h1>
      <p className="mt-2 text-muted">Pick a note from the sidebar, or start a new one. Link notes by typing <code className="font-mono text-sm bg-raised px-1.5 py-0.5 rounded">[[Note title]]</code>.</p>
      {error && <div className="mt-8"><ErrorNote message={error} /></div>}
      {!loading && !error && notes.length > 0 && (
        <div className="mt-10 grid sm:grid-cols-2 gap-3">
          {notes.slice(0, 8).map(n => (
            <Link key={n.id} to={`/notes/${n.id}`} className="rounded-xl border border-line bg-surface p-4 hover:border-accent transition-colors">
              <p className="font-medium truncate">{n.title || 'Untitled'}</p>
              <p className="mt-1 text-sm text-muted line-clamp-2 min-h-[2.5em]">{n.content.replace(/[#*>`[\]]/g, '').slice(0, 140) || 'Empty note'}</p>
              <p className="mt-3 text-xs text-dim">v{n.version} · {ago(n.updated_at)}</p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
