export function LogoMark({ className = "size-7" }: { className?: string }) {
  // a scope reticle with a price tick: "keeping an eye on competitor prices"
  return (
    <svg viewBox="0 0 32 32" className={className} aria-hidden>
      <rect width="32" height="32" rx="9" className="fill-primary" />
      <circle cx="16" cy="16" r="8.5" fill="none" strokeWidth="2.2" className="stroke-primary-foreground" />
      <path d="M16 4.5v5M16 22.5v5M4.5 16h5M22.5 16h5" strokeWidth="2.2" strokeLinecap="round" className="stroke-primary-foreground/70" />
      <circle cx="16" cy="16" r="2.6" className="fill-primary-foreground" />
    </svg>
  );
}

export function Logo() {
  return (
    <span className="flex items-center gap-2">
      <LogoMark />
      <span className="text-[15px] font-semibold tracking-tight">Rivalscope</span>
    </span>
  );
}
