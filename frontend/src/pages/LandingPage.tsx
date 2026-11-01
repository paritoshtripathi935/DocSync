/**
 * LandingPage — public marketing page for signed-out visitors. CTAs call
 * `onStart` (Clerk sign-in); without auth configured they link to the repo.
 */
import { useState, type ReactNode } from 'react';
import { ArrowRight, ChevronDown, FileText, GitBranch, History, Link2, Search, Zap } from 'lucide-react';
import Logo from '../components/Logo';
import ThemeToggle from '../components/ThemeToggle';

const REPO = 'https://github.com/paritoshtripathi935/DocSync';

const FEATURES: [typeof FileText, string, string][] = [
  [FileText, 'Markdown, nothing else', 'Headings, lists, tables, task lists and code blocks. Your notes stay plain text you can take anywhere.'],
  [Link2, 'Wiki links & backlinks', 'Type [[Another note]] to link it. Every note shows what links back to it, so ideas find each other.'],
  [History, 'A version for every save', 'Each save is a numbered version. Browse the timeline and restore any earlier text in one click.'],
  [Search, 'Search everything', 'Find notes by title, body or tag from the sidebar, as you type.'],
  [Zap, 'Fast reads', 'Notes are cached in Redis, so opening one you just edited is instant.'],
  [GitBranch, 'Open source', 'FastAPI + MongoDB backend and this React frontend, all on GitHub.'],
];

const ROADMAP: [string, string][] = [
  ['Real-time collaboration', 'Edit the same note together, with presence and conflict-free merging.'],
  ['AI over your notes', 'Summaries, suggested links and questions answered from your own knowledge base.'],
  ['Graph view', 'See how your notes connect, and which ones are orphaned.'],
];

const FAQS: [string, string][] = [
  ['Is it free?', 'Yes. DocSync is an open-source beta; there is nothing to pay for.'],
  ['How do links work?', 'Wrap a note title in double brackets: [[Weekly review]]. If the note doesn’t exist yet, clicking the link creates it.'],
  ['Can I undo a change?', 'Every save becomes a version. Open History on any note to view or restore an older version.'],
  ['Is it like Obsidian?', 'Same idea — linked markdown notes — but in the browser, with server-side history. Collaboration and AI features are on the roadmap.'],
];

function Cta({ onStart, children, ghost = false }: { onStart?: () => void; children: ReactNode; ghost?: boolean }) {
  const cls = ghost ? 'border border-line text-fg hover:bg-hover' : 'bg-accent text-ink hover:brightness-110';
  const base = `inline-flex items-center justify-center gap-2 rounded-full px-6 h-11 text-small font-semibold transition-all cursor-pointer ${cls}`;
  return onStart ? <button onClick={onStart} className={base}>{children}</button> : <a href={REPO} className={base}>{children}</a>;
}

const Eyebrow = ({ children }: { children: ReactNode }) => (
  <p className="text-caption font-semibold uppercase tracking-wider text-accent mb-3">{children}</p>
);
const H2 = ({ children }: { children: ReactNode }) => (
  <h2 className="font-serif text-h2 md:text-h1 font-medium">{children}</h2>
);
const W = ({ children }: { children: ReactNode }) => (
  <span className="text-accent underline underline-offset-4 decoration-accent/40">{children}</span>
);

/** Editor mock: a note, its rendered links, and the backlinks panel. */
function EditorMock() {
  return (
    <div className="rounded-2xl border border-line bg-surface shadow-2xl shadow-black/20 overflow-hidden grid sm:grid-cols-[150px_1fr_170px] text-small">
      <div className="hidden sm:block border-r border-line p-3 space-y-1">
        {['Roadmap', 'Project kickoff', 'Auth rollout', 'Pricing notes', 'Weekly review'].map((t, i) => (
          <div key={t} className={`rounded-md px-3 py-2 truncate ${i === 1 ? 'bg-accent-soft text-fg font-medium' : 'text-muted'}`}>{t}</div>
        ))}
      </div>
      <div className="p-6 min-w-0">
        <p className="text-caption text-dim">v4 · saved</p>
        <h3 className="mt-2 font-serif text-h3 font-medium">Project kickoff</h3>
        <div className="mt-4 font-serif text-body leading-7 space-y-3 text-fg/90">
          <p>Ship the beta once <W>Auth rollout</W> is done. Pricing questions are parked in <W>Pricing notes</W>.</p>
          <ul className="list-disc pl-6 space-y-1">
            <li>Write the onboarding guide</li>
            <li>Review last week in <W>Weekly review</W></li>
          </ul>
        </div>
      </div>
      <div className="hidden sm:block border-l border-line p-4 space-y-6 text-caption">
        <div>
          <p className="font-semibold text-dim uppercase tracking-wider">Backlinks</p>
          <p className="mt-2 text-accent">Roadmap</p><p className="mt-1 text-accent">Weekly review</p>
        </div>
        <div>
          <p className="font-semibold text-dim uppercase tracking-wider">History</p>
          {['v4 · now', 'v3 · 2h ago', 'v2 · yesterday'].map(v => <p key={v} className="mt-2 text-muted">{v}</p>)}
        </div>
      </div>
    </div>
  );
}

export default function LandingPage({ onStart }: { onStart?: () => void }) {
  const [open, setOpen] = useState<number | null>(0);
  return (
    <div className="min-h-screen bg-bg text-fg">
      <header className="sticky top-0 z-20 border-b border-line bg-bg/80 backdrop-blur">
        <nav className="mx-auto max-w-6xl px-4 sm:px-6 h-16 flex items-center justify-between">
          <Logo />
          <div className="hidden md:flex items-center gap-8 text-small text-muted">
            <a href="#features" className="py-2 hover:text-fg">Features</a>
            <a href="#roadmap" className="py-2 hover:text-fg">Roadmap</a>
            <a href="#faq" className="py-2 hover:text-fg">FAQ</a>
            <a href={REPO} className="py-2 hover:text-fg">GitHub</a>
          </div>
          <div className="flex items-center gap-2">
            <ThemeToggle />
            {onStart && <button onClick={onStart} className="hidden sm:inline text-small text-muted hover:text-fg px-3 cursor-pointer">Sign in</button>}
            <Cta onStart={onStart}>Start writing</Cta>
          </div>
        </nav>
      </header>

      <main>
        <section className="mx-auto max-w-6xl px-4 sm:px-6 pt-16 md:pt-24 pb-24 text-center">
          <Eyebrow>A markdown knowledge base</Eyebrow>
          <h1 className="font-serif text-h1 sm:text-display font-medium max-w-3xl mx-auto">
            Your notes, <em className="text-accent">linked</em> and versioned.
          </h1>
          <p className="mt-6 text-sub text-muted max-w-xl mx-auto leading-7">
            Write in markdown, connect ideas with [[wiki links]], and never lose a sentence —
            every save is a version you can go back to.
          </p>
          <div className="mt-8 flex flex-wrap justify-center gap-3">
            <Cta onStart={onStart}>Start writing — it's free <ArrowRight size={16} /></Cta>
            <Cta ghost>View source</Cta>
          </div>
          <div className="mt-16 text-left max-w-4xl mx-auto"><EditorMock /></div>
        </section>

        <section id="features" className="border-t border-line bg-surface">
          <div className="mx-auto max-w-6xl px-4 sm:px-6 py-24">
            <Eyebrow>What's inside</Eyebrow>
            <H2>Everything a second brain needs. Nothing it doesn't.</H2>
            <div className="mt-12 grid sm:grid-cols-2 lg:grid-cols-3 gap-x-12 gap-y-12">
              {FEATURES.map(([Icon, title, body]) => (
                <div key={title}>
                  <span className="grid place-items-center h-10 w-10 rounded-lg bg-accent-soft"><Icon size={18} className="text-accent" /></span>
                  <h3 className="mt-4 font-semibold">{title}</h3>
                  <p className="mt-2 text-body text-muted">{body}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section id="roadmap" className="mx-auto max-w-6xl px-4 sm:px-6 py-24 grid lg:grid-cols-[1fr_1.4fr] gap-12">
          <div>
            <Eyebrow>On the roadmap</Eyebrow>
            <H2>Where DocSync is headed.</H2>
            <p className="mt-4 text-muted leading-7">Not shipped yet — this is what's being built next.</p>
          </div>
          <ol className="divide-y divide-line border-y border-line">
            {ROADMAP.map(([title, body], i) => (
              <li key={title} className="py-6 grid grid-cols-[40px_1fr] gap-2">
                <span className="font-mono text-small text-dim">0{i + 1}</span>
                <div><h3 className="font-semibold">{title}</h3><p className="mt-1 text-body text-muted">{body}</p></div>
              </li>
            ))}
          </ol>
        </section>

        <section id="faq" className="border-t border-line bg-surface">
          <div className="mx-auto max-w-3xl px-4 sm:px-6 py-24">
            <Eyebrow>FAQ</Eyebrow>
            <H2>Questions, answered.</H2>
            <div className="mt-12 divide-y divide-line border-y border-line">
              {FAQS.map(([q, a], i) => (
                <div key={q}>
                  <button onClick={() => setOpen(open === i ? null : i)} aria-expanded={open === i}
                    className="w-full flex items-center justify-between gap-4 py-6 text-left font-medium cursor-pointer">
                    {q}<ChevronDown size={18} className={`shrink-0 text-dim transition-transform ${open === i ? 'rotate-180' : ''}`} />
                  </button>
                  {open === i && <p className="pb-6 -mt-1 text-muted leading-7">{a}</p>}
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="mx-auto max-w-6xl px-4 sm:px-6 py-24 text-center">
          <H2>Start your knowledge base today.</H2>
          <p className="mt-4 text-muted">Free while in beta. Your first note is one click away.</p>
          <div className="mt-8"><Cta onStart={onStart}>Start writing <ArrowRight size={16} /></Cta></div>
        </section>
      </main>

      <footer className="border-t border-line">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 py-12 flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between text-small text-dim">
          <Logo size={22} />
          <div className="flex gap-6">
            <a href={REPO} className="hover:text-fg">Source code</a>
            <a href="https://www.paritosh.online/" className="hover:text-fg">Built by Paritosh</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
