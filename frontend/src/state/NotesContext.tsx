/**
 * Holds the note list for the sidebar, backlinks and wiki-link resolution.
 * shortcut: loads at most 100 notes (the API's page cap); paginate once
 * someone has more.
 */
import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react';
import { useApi } from '../services/api';
import type { Note } from '../types';

interface NotesCtx {
  notes: Note[];
  loading: boolean;
  error: string | null;
  reload: () => Promise<void>;
  upsert: (n: Note) => void;
  remove: (id: number) => void;
  create: (title: string, content?: string) => Promise<Note>;
}

const Ctx = createContext<NotesCtx | null>(null);

const byUpdated = (a: Note, b: Note) => (b.updated_at ?? '').localeCompare(a.updated_at ?? '');

export function NotesProvider({ children }: { children: ReactNode }) {
  const api = useApi();
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(async () => {
    setLoading(true); setError(null);
    try { setNotes((await api.listNotes()).items.sort(byUpdated)); }
    catch (e) { setError((e as Error).message); }
    finally { setLoading(false); }
  }, [api]);

  useEffect(() => { reload(); }, [reload]);

  const upsert = useCallback((n: Note) =>
    setNotes(prev => [n, ...prev.filter(p => p.id !== n.id)].sort(byUpdated)), []);
  const remove = useCallback((id: number) => setNotes(prev => prev.filter(p => p.id !== id)), []);
  const create = useCallback(async (title: string, content = '') => {
    const n = await api.createNote(title, content);
    upsert(n);
    return n;
  }, [api, upsert]);

  return <Ctx.Provider value={{ notes, loading, error, reload, upsert, remove, create }}>{children}</Ctx.Provider>;
}

export function useNotes() {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error('useNotes must be used inside NotesProvider');
  return ctx;
}
