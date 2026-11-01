export default function Logo({ size = 28 }: { size?: number }) {
  return (
    <span className="inline-flex items-center gap-3">
      <svg width={size} height={size} viewBox="0 0 32 32" aria-hidden>
        <rect width="32" height="32" rx="8" className="fill-raised stroke-line" strokeWidth="1" />
        <path d="M10 11L16 22M22 10L16 22M10 11L22 10" className="stroke-accent" strokeWidth="1.5" opacity=".55" />
        <circle cx="10" cy="11" r="3" className="fill-accent" />
        <circle cx="22" cy="10" r="2.5" className="fill-accent" opacity=".75" />
        <circle cx="16" cy="22" r="3.5" className="fill-accent" />
      </svg>
      <span className="font-serif font-semibold text-sub">DocSync</span>
    </span>
  );
}
