/**
 * Split-screen sign-in. Left: a note with live-looking wiki links and its
 * backlinks — the product in one glance. Right: Clerk.
 */
import { SignIn } from '@clerk/clerk-react';
import { ArrowLeft } from 'lucide-react';
import Logo from './Logo';

export default function LoginPage({ onBack }: { onBack: () => void }) {
  return (
    <div className="min-h-screen grid lg:grid-cols-[1.2fr_1fr] bg-bg">
      <aside className="hidden lg:flex flex-col justify-between p-12 border-r border-line bg-surface">
        <Logo />
        <div className="max-w-md">
          <p className="font-serif text-4xl leading-tight">Write it once.<br /><em className="text-accent">Find it from everywhere.</em></p>
          <div className="mt-8 rounded-xl border border-line bg-bg p-6 font-serif text-[17px] leading-relaxed">
            <p className="font-sans text-xs text-dim mb-3">Project kickoff · v4</p>
            Ship the beta after <span className="text-accent underline underline-offset-4">Auth rollout</span> lands.
            Open questions live in <span className="text-accent underline underline-offset-4">Pricing notes</span>.
            <p className="mt-5 pt-4 border-t border-line font-sans text-xs text-dim">2 backlinks · Weekly review, Roadmap</p>
          </div>
        </div>
        <p className="text-xs text-dim">Markdown · wiki links · a version for every save</p>
      </aside>
      <main className="flex flex-col items-center justify-center gap-6 p-6">
        <div className="w-full max-w-sm flex items-center justify-between">
          <button onClick={onBack} className="inline-flex items-center gap-1.5 text-sm text-muted hover:text-fg cursor-pointer">
            <ArrowLeft size={15} /> Back
          </button>
          <span className="lg:hidden"><Logo size={24} /></span>
        </div>
        <SignIn routing="hash" />
      </main>
    </div>
  );
}
