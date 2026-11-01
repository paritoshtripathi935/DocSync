import { useEffect, useState } from 'react';
import { NavLink, Outlet, useMatch, useNavigate } from 'react-router-dom';
import { UserButton } from '@clerk/clerk-react';
import { Loader2, Plus, Search, X } from 'lucide-react';
import Logo from './Logo';
import ThemeToggle from './ThemeToggle';
import { useNotes } from '../state/NotesContext';
import { useApi } from '../services/api';
import { ago } from '../utils/time';
import type { Note } from '../types';

export default function AppLayout() {
  const api = useApi();
  const navigate = useNavigate();
  const onNote = useMatch('/notes/:noteId');
  const { notes, loading, create } = useNotes();
  const [q, setQ] = useState('');
  const [results, setResults] = useState<Note[] | null>(null);
  const [creating, setCreating] = useState(false);

  // Server-side search, debounced; empty query falls back to the full list.
  useEffect(() => {
    if (!q.trim()) return;
    const id = window.setTimeout(() => {
      api.listNotes(q.trim(), 50).then(r => setResults(r.items)).catch(() => setResults([]));
    }, 250);
    return () => window.clearTimeout(id);
  }, [q, api]);

  async function newNote() {
    setCreating(true);
    try { navigate(`/notes/${(await create('Untitled')).id}?new=1`); }
    catch (e) { alert((e as Error).message); }
    finally { setCreating(false); }
  }

  const searching = q.trim() !== '' && results !== null;
  const list = searching ? results : notes;
  const item = ({ isActive }: { isActive: boolean }) =>
    `block rounded-lg px-3 py-2 transition-colors ${isActive ? 'bg-accent-soft' : 'hover:bg-hover'}`;

  return (
    <div className="h-screen md:grid md:grid-cols-[272px_1fr] overflow-hidden">
      {/* On phones the sidebar is the home screen; a note takes the full width. */}
      <aside className={`${onNote ? 'hidden md:flex' : 'flex'} h-full flex-col border-r border-line bg-surface`}>
        <div className="flex items-center justify-between px-4 h-14">
          <Logo size={24} />
          <ThemeToggle />
        </div>
        <div className="px-3 space-y-2">
          <button onClick={newNote} disabled={creating}
            className="w-full inline-flex items-center justify-center gap-2 rounded-lg bg-accent text-ink h-9 text-sm font-semibold cursor-pointer disabled:opacity-60">
            {creating ? <Loader2 size={15} className="animate-spin" /> : <Plus size={16} />} New note
          </button>
          <div className="relative">
            <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-dim" />
            <label htmlFor="search" className="sr-only">Search notes</label>
            <input id="search" value={q} onChange={e => setQ(e.target.value)} placeholder="Search notes"
              className="w-full rounded-lg bg-raised border border-line pl-9 pr-8 h-9 text-sm outline-none focus:border-accent placeholder:text-dim" />
            {q && <button onClick={() => setQ('')} aria-label="Clear search" className="absolute right-2 top-1/2 -translate-y-1/2 text-dim hover:text-fg cursor-pointer"><X size={15} /></button>}
          </div>
        </div>
        <p className="px-4 pt-5 pb-2 text-[11px] font-semibold uppercase tracking-wider text-dim">
          {searching ? `${list.length} result${list.length === 1 ? '' : 's'}` : 'Notes'}
        </p>
        <nav className="flex-1 overflow-y-auto px-2 pb-3 space-y-0.5">
          {loading && !searching && <p className="px-3 py-2 text-sm text-dim flex items-center gap-2"><Loader2 size={14} className="animate-spin" /> Loading…</p>}
          {!loading && list.length === 0 && <p className="px-3 py-2 text-sm text-dim">{searching ? 'Nothing matches.' : 'No notes yet.'}</p>}
          {list.map(n => (
            <NavLink key={n.id} to={`/notes/${n.id}`} className={item}>
              <span className="block text-sm font-medium truncate">{n.title || 'Untitled'}</span>
              <span className="block text-xs text-dim truncate">
                {ago(n.updated_at)}{n.tags.length > 0 && ` · ${n.tags.map(t => `#${t}`).join(' ')}`}
              </span>
            </NavLink>
          ))}
        </nav>
        <div className="border-t border-line px-4 h-14 flex items-center"><UserButton showName /></div>
      </aside>
      <main className={`${onNote ? 'block' : 'hidden md:block'} h-full overflow-y-auto min-w-0`}><Outlet /></main>
    </div>
  );
}
