import { useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from 'react';
import { Link, useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { ArrowLeft, Eye, Info, Loader2, PenLine, RotateCcw, Trash2, X } from 'lucide-react';
import { useApi } from '../services/api';
import { useNotes } from '../state/NotesContext';
import MarkdownView from '../components/MarkdownView';
import ErrorNote from '../components/ErrorNote';
import { linksTo, sameTitle, wikiTargets } from '../utils/wiki';
import { ago } from '../utils/time';
import type { Note, NoteVersion } from '../types';

const AUTOSAVE_MS = 1500;

interface Draft { title: string; content: string; tags: string }

const parseTags = (s: string) => [...new Set(s.split(',').map(t => t.trim().replace(/^#/, '')).filter(Boolean))];

function diff(note: Note, d: Draft): Partial<Pick<Note, 'title' | 'content' | 'tags'>> {
  const out: Partial<Pick<Note, 'title' | 'content' | 'tags'>> = {};
  const title = d.title.trim() || 'Untitled';
  if (title !== note.title) out.title = title;
  if (d.content !== note.content) out.content = d.content;
  const tags = parseTags(d.tags);
  if (tags.join('\u0000') !== note.tags.join('\u0000')) out.tags = tags;
  return out;
}

export default function NotePage() {
  const id = Number(useParams().noteId);
  const [params] = useSearchParams();
  const startInWrite = useRef(params.get('new') === '1');
  const api = useApi();
  const navigate = useNavigate();
  const { notes, upsert, remove, create } = useNotes();

  const [note, setNote] = useState<Note | null>(null);
  const [draft, setDraft] = useState<Draft>({ title: '', content: '', tags: '' });
  const [loadError, setLoadError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [mode, setMode] = useState<'write' | 'preview'>('write');
  const [history, setHistory] = useState<NoteVersion[]>([]);
  const [viewing, setViewing] = useState<NoteVersion | null>(null);
  const [panelOpen, setPanelOpen] = useState(false);
  const idRef = useRef(id);

  useEffect(() => {
    idRef.current = id;
    let cancelled = false;
    setNote(null); setLoadError(null); setSaveError(null); setHistory([]);
    api.getNote(id).then(n => {
      if (cancelled) return;
      setNote(n);
      // 'Untitled' is the server-side placeholder; show an empty field instead
      setDraft({ title: n.title === 'Untitled' ? '' : n.title, content: n.content, tags: n.tags.join(', ') });
      setMode(startInWrite.current || !n.content ? 'write' : 'preview');
      startInWrite.current = false;
    }).catch(e => { if (!cancelled) setLoadError((e as Error).message); });
    return () => { cancelled = true; };
  }, [id, api]);

  const loadHistory = useCallback(() => {
    api.getHistory(id).then(h => { if (idRef.current === id) setHistory(h); }).catch(() => {});
  }, [api, id]);
  useEffect(() => { loadHistory(); }, [loadHistory]);

  const changes = useMemo(() => (note ? diff(note, draft) : {}), [note, draft]);
  const dirty = Object.keys(changes).length > 0;

  const save = useCallback(async () => {
    if (!note || !dirty) return;
    setSaving(true); setSaveError(null);
    try {
      const saved = await api.updateNote(note.id, changes);
      upsert(saved);
      if (idRef.current === saved.id) { setNote(saved); loadHistory(); }
    } catch (e) {
      if (idRef.current === note.id) setSaveError((e as Error).message);
    } finally {
      setSaving(false);
    }
  }, [api, note, dirty, changes, upsert, loadHistory]);

  // Autosave after a pause in typing.
  useEffect(() => {
    if (!dirty || saving) return;
    const t = window.setTimeout(save, AUTOSAVE_MS);
    return () => window.clearTimeout(t);
  }, [dirty, saving, save]);

  // Flush pending edits when leaving this note.
  const saveRef = useRef(save);
  useEffect(() => { saveRef.current = save; }, [save]);
  useEffect(() => () => { saveRef.current(); }, [id]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 's') { e.preventDefault(); save(); }
      if (e.key === 'Escape') setViewing(null);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [save]);

  async function openOrCreate(title: string) {
    const existing = notes.find(n => sameTitle(n.title, title));
    try { navigate(`/notes/${(existing ?? await create(title)).id}`); }
    catch (e) { setSaveError((e as Error).message); }
  }

  async function del() {
    if (!note || !confirm(`Delete "${note.title}"? This can't be undone.`)) return;
    try {
      await api.deleteNote(note.id);
      setNote(null); // nothing left to flush
      remove(note.id);
      navigate('/');
    } catch (e) { setSaveError((e as Error).message); }
  }

  if (loadError) return <div className="p-10 max-w-xl"><ErrorNote message={loadError} /><Link to="/" className="mt-4 inline-block text-sm text-accent">Back to notes</Link></div>;
  if (!note) return <p className="p-10 flex items-center gap-2 text-sm text-dim"><Loader2 size={15} className="animate-spin" /> Opening note…</p>;

  const title = draft.title.trim() || 'Untitled';
  const backlinks = notes.filter(n => n.id !== id && linksTo(n.content, title));
  const outgoing = wikiTargets(draft.content).map(t => ({ t, target: notes.find(n => sameTitle(n.title, t)) }));
  const status = saving ? 'Saving…' : saveError ? 'Not saved' : dirty ? 'Unsaved changes' : `Saved · v${note.version}`;

  const tab = (m: 'write' | 'preview', Icon: typeof Eye, label: string) => (
    <button onClick={() => setMode(m)} aria-pressed={mode === m}
      className={`inline-flex items-center gap-1.5 rounded-md px-2.5 h-7 text-xs font-medium cursor-pointer ${mode === m ? 'bg-surface text-fg shadow-sm' : 'text-muted hover:text-fg'}`}>
      <Icon size={13} /> {label}
    </button>
  );

  return (
    <div className="min-h-full flex flex-col">
      <header className="sticky top-0 z-10 flex items-center gap-2 border-b border-line bg-bg/90 backdrop-blur px-4 h-14">
        <Link to="/" aria-label="All notes" className="md:hidden h-9 w-9 grid place-items-center rounded-lg text-muted hover:bg-hover"><ArrowLeft size={17} /></Link>
        <span role="status" className={`text-xs ${saveError ? 'text-danger' : 'text-dim'} truncate`}>{status}</span>
        <div className="ml-auto flex items-center gap-1">
          <div className="flex rounded-lg bg-raised p-0.5">{tab('write', PenLine, 'Write')}{tab('preview', Eye, 'Preview')}</div>
          <button onClick={() => setPanelOpen(o => !o)} aria-label="Links and history" aria-pressed={panelOpen}
            className="xl:hidden h-9 w-9 grid place-items-center rounded-lg text-muted hover:text-fg hover:bg-hover cursor-pointer"><Info size={17} /></button>
          <button onClick={del} aria-label="Delete note" className="h-9 w-9 grid place-items-center rounded-lg text-muted hover:text-danger hover:bg-hover cursor-pointer"><Trash2 size={16} /></button>
        </div>
      </header>

      {saveError && <div className="px-6 pt-4"><ErrorNote message={saveError} /></div>}

      <div className="flex-1 xl:grid xl:grid-cols-[1fr_288px]">
        <article className="mx-auto w-full max-w-3xl px-6 sm:px-10 py-10">
          <label htmlFor="title" className="sr-only">Title</label>
          <input id="title" value={draft.title} onChange={e => setDraft(d => ({ ...d, title: e.target.value }))} placeholder="Untitled"
            className="w-full bg-transparent font-serif text-[34px] sm:text-[40px] font-medium leading-tight outline-none placeholder:text-dim" />
          <label htmlFor="tags" className="sr-only">Tags</label>
          <input id="tags" value={draft.tags} onChange={e => setDraft(d => ({ ...d, tags: e.target.value }))} placeholder="Add tags, comma-separated"
            className="mt-2 w-full bg-transparent text-sm text-muted outline-none placeholder:text-dim" />
          <div className="mt-8">
            {mode === 'write' ? (
              <>
                <label htmlFor="body" className="sr-only">Note body (markdown)</label>
                <textarea id="body" value={draft.content} autoFocus={!draft.content}
                  onChange={e => setDraft(d => ({ ...d, content: e.target.value }))}
                  placeholder={'Start writing in markdown…\n\nLink another note with [[Its title]].'}
                  className="w-full min-h-[60vh] [field-sizing:content] resize-none bg-transparent font-mono text-[14px] leading-7 outline-none placeholder:text-dim" />
              </>
            ) : draft.content.trim() ? (
              <MarkdownView content={draft.content} notes={notes} onMissing={openOrCreate} />
            ) : (
              <p className="text-dim">Nothing here yet. <button onClick={() => setMode('write')} className="text-accent cursor-pointer">Start writing</button>.</p>
            )}
          </div>
        </article>

        <aside className={`${panelOpen ? 'block' : 'hidden'} xl:block border-t xl:border-t-0 xl:border-l border-line px-5 py-8 space-y-8 text-sm`}>
          <Panel title={`Backlinks · ${backlinks.length}`}>
            {backlinks.length === 0 ? <Empty>No notes link here yet. Type [[{title}]] in another note.</Empty> :
              backlinks.map(n => <Link key={n.id} to={`/notes/${n.id}`} className="block py-1 text-accent hover:underline truncate">{n.title}</Link>)}
          </Panel>
          <Panel title={`Links · ${outgoing.length}`}>
            {outgoing.length === 0 ? <Empty>Link a note with [[Its title]].</Empty> :
              outgoing.map(({ t, target }) => (
                <button key={t} onClick={() => openOrCreate(t)}
                  className={`block w-full text-left py-1 truncate cursor-pointer hover:underline ${target ? 'text-accent' : 'text-dim'}`}
                  title={target ? `Open ${t}` : `Create "${t}"`}>
                  {t}{!target && ' · create'}
                </button>
              ))}
          </Panel>
          <Panel title="History">
            {history.length === 0 ? <Empty>No versions yet.</Empty> : (
              <ol className="space-y-0.5">
                {history.map(v => (
                  <li key={v._id ?? v.version}>
                    <button onClick={() => setViewing(v)} className="w-full flex justify-between gap-2 rounded-md px-2 py-1.5 -mx-2 hover:bg-hover cursor-pointer">
                      <span className={v.version === note.version ? 'text-fg font-medium' : 'text-muted'}>v{v.version}{v.version === note.version && ' · current'}</span>
                      <span className="text-xs text-dim">{ago(v.timestamp)}</span>
                    </button>
                  </li>
                ))}
              </ol>
            )}
          </Panel>
        </aside>
      </div>

      {viewing && (
        <div role="dialog" aria-modal="true" aria-label={`Version ${viewing.version}`} onClick={() => setViewing(null)}
          className="fixed inset-0 z-30 bg-black/50 grid place-items-center p-4">
          <div onClick={e => e.stopPropagation()} className="w-full max-w-2xl max-h-[85vh] flex flex-col rounded-2xl border border-line bg-surface shadow-2xl">
            <div className="flex items-center justify-between gap-3 px-5 h-14 border-b border-line">
              <p className="text-sm"><span className="font-semibold">Version {viewing.version}</span> <span className="text-dim">· {ago(viewing.timestamp)}</span></p>
              <button onClick={() => setViewing(null)} aria-label="Close" className="h-8 w-8 grid place-items-center rounded-lg text-muted hover:bg-hover cursor-pointer"><X size={16} /></button>
            </div>
            <div className="overflow-y-auto px-6 py-6">
              {viewing.title && <h2 className="font-serif text-2xl font-medium mb-4">{viewing.title}</h2>}
              {viewing.content.trim() ? <MarkdownView content={viewing.content} notes={notes} /> : <p className="text-dim">Empty.</p>}
            </div>
            <div className="flex justify-end gap-2 px-5 py-3 border-t border-line">
              <button onClick={() => setViewing(null)} className="rounded-lg px-4 h-9 text-sm hover:bg-hover cursor-pointer">Close</button>
              <button disabled={viewing.version === note.version}
                onClick={() => { setDraft(d => ({ ...d, content: viewing.content, title: viewing.title === undefined ? d.title : viewing.title === 'Untitled' ? '' : viewing.title })); setViewing(null); }}
                className="inline-flex items-center gap-2 rounded-lg bg-accent text-ink px-4 h-9 text-sm font-semibold cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed">
                <RotateCcw size={14} /> Restore this version
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

const Panel = ({ title, children }: { title: string; children: ReactNode }) => (
  <section><h2 className="text-[11px] font-semibold uppercase tracking-wider text-dim mb-2">{title}</h2>{children}</section>
);
const Empty = ({ children }: { children: ReactNode }) => <p className="text-xs text-dim leading-relaxed">{children}</p>;
