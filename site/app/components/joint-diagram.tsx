// Blueprint line-work (D-011): a mortise-and-tenon joint pinned by a
// treenail peg — the object the product is named for, drawn as a drafting
// annotation. Structural strokes use the line-work token; the peg is the
// oak accent. Decorative, so hidden from assistive tech.
export function JointDiagram({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 320 280"
      fill="none"
      role="img"
      aria-label="A mortise-and-tenon timber joint pinned by a round treenail peg, drawn in blueprint line-work."
      style={{ width: '100%', height: 'auto', maxWidth: '30rem' }}
    >
      {/* center lines */}
      <g stroke="var(--tn-line)" strokeWidth="0.75" strokeDasharray="3 4" opacity="0.6">
        <line x1="160" y1="8" x2="160" y2="272" />
        <line x1="16" y1="150" x2="304" y2="150" />
      </g>

      {/* vertical member (mortised) */}
      <g stroke="var(--tn-line)" strokeWidth="1.5" strokeLinejoin="round">
        <rect x="120" y="20" width="80" height="240" fill="var(--tn-surface)" rx="1" />
        {/* mortise pocket */}
        <rect x="140" y="118" width="40" height="64" fill="var(--tn-bg)" rx="1" />
      </g>

      {/* horizontal member with tenon inserted */}
      <g stroke="var(--tn-line)" strokeWidth="1.5" strokeLinejoin="round">
        <path
          d="M16 118 H140 V118 H180 V182 H140 V182 H16 Z"
          fill="var(--tn-surface-raised)"
        />
        <line x1="140" y1="118" x2="140" y2="182" strokeDasharray="2 3" opacity="0.7" />
      </g>

      {/* the treenail peg — oak accent, driven through the joint */}
      <g>
        <circle cx="160" cy="150" r="15" fill="var(--tn-accent)" stroke="var(--tn-accent-strong)" strokeWidth="1.5" />
        <circle cx="160" cy="150" r="6" fill="var(--tn-accent-strong)" opacity="0.55" />
      </g>

      {/* dimension annotation */}
      <g stroke="var(--tn-line)" strokeWidth="0.75" opacity="0.8">
        <line x1="224" y1="118" x2="224" y2="182" />
        <line x1="220" y1="118" x2="228" y2="118" />
        <line x1="220" y1="182" x2="228" y2="182" />
      </g>
      <text
        x="234"
        y="154"
        fill="var(--tn-muted)"
        fontFamily="var(--font-mono)"
        fontSize="11"
        letterSpacing="0.04em"
      >
        peg Ø
      </text>
    </svg>
  );
}
