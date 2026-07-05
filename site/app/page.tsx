import Link from 'next/link';
import { ThemeToggle } from './components/theme-toggle';
import { JointDiagram } from './components/joint-diagram';

// Foundation hero (T-005) — proves the craft-meets-engineering design
// system (D-011) end to end in both themes. The full eight-section,
// pain-led narrative (D-009) is T-007; this establishes the system.
const RECORDS = [
  { id: 'D-001', kind: 'decision' },
  { id: 'R-002', kind: 'risk' },
  { id: 'T-003', kind: 'task' },
];

export default function HomePage() {
  return (
    <main className="tn-blueprint-grid" style={{ minHeight: '100dvh' }}>
      <div
        style={{
          maxWidth: '72rem',
          margin: '0 auto',
          padding: 'clamp(1.25rem, 3vw, 2rem)',
          display: 'flex',
          flexDirection: 'column',
          minHeight: '100dvh',
        }}
      >
        <header
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '1rem',
          }}
        >
          <span
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.6rem',
              fontWeight: 600,
              fontSize: '1.05rem',
              letterSpacing: '-0.01em',
            }}
          >
            <span
              aria-hidden
              style={{
                width: '0.7rem',
                height: '0.7rem',
                borderRadius: '50%',
                background: 'var(--tn-accent)',
                boxShadow: '0 0 0 3px var(--tn-accent-wash)',
              }}
            />
            Treenail
          </span>
          <nav
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 'clamp(0.75rem, 2vw, 1.5rem)',
              fontSize: '0.9rem',
            }}
          >
            <Link href="/docs" style={{ color: 'var(--tn-muted)' }}>
              Docs
            </Link>
            <Link href="/contact" style={{ color: 'var(--tn-muted)' }}>
              Contact
            </Link>
            <ThemeToggle />
          </nav>
        </header>

        <section
          className="tn-rise"
          style={{
            flex: 1,
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 22rem), 1fr))',
            gap: 'clamp(2rem, 5vw, 4rem)',
            alignItems: 'center',
            padding: 'clamp(2rem, 6vw, 4.5rem) 0',
          }}
        >
          <div style={{ maxWidth: '34rem' }}>
            <h1
              style={{
                margin: 0,
                fontSize: 'clamp(2.4rem, 6vw, 4rem)',
                lineHeight: 1.02,
                letterSpacing: '-0.03em',
                textWrap: 'balance',
                fontWeight: 680,
              }}
            >
              Durable planning joinery for your coding agent.
            </h1>
            <p
              style={{
                marginTop: '1.25rem',
                marginBottom: 0,
                fontSize: 'clamp(1rem, 2vw, 1.15rem)',
                lineHeight: 1.6,
                color: 'var(--tn-muted)',
                maxWidth: '38ch',
                textWrap: 'pretty',
              }}
            >
              Decisions, risks, and tasks kept as a versioned record — pegged
              into your repo, not lost in chat history. The joint becomes the
              structure.
            </p>

            <div
              style={{
                marginTop: '2rem',
                display: 'flex',
                gap: '1.25rem 1.75rem',
                flexWrap: 'wrap',
                alignItems: 'center',
              }}
            >
              {RECORDS.map((r) => (
                <span
                  key={r.id}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    fontSize: '0.85rem',
                    color: 'var(--tn-muted)',
                  }}
                >
                  <span className="tn-id">{r.id}</span>
                  {r.kind}
                </span>
              ))}
            </div>

            <div
              style={{
                marginTop: '2.5rem',
                display: 'flex',
                gap: '0.85rem',
                flexWrap: 'wrap',
              }}
            >
              <Link
                href="/docs"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  padding: '0.7rem 1.25rem',
                  borderRadius: '2px',
                  background: 'var(--tn-accent)',
                  color: 'var(--tn-accent-fg)',
                  fontWeight: 550,
                  fontSize: '0.95rem',
                }}
              >
                Read the docs
              </Link>
              <Link
                href="/contact"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  padding: '0.7rem 1.25rem',
                  borderRadius: '2px',
                  border: '1px solid var(--tn-border)',
                  color: 'var(--tn-ink)',
                  fontWeight: 550,
                  fontSize: '0.95rem',
                }}
              >
                Get in touch
              </Link>
            </div>
          </div>

          <div
            className="tn-ticks"
            style={{
              padding: 'clamp(1.5rem, 4vw, 2.5rem)',
              display: 'flex',
              justifyContent: 'center',
            }}
          >
            <JointDiagram />
          </div>
        </section>

        <footer
          style={{
            paddingTop: '1.5rem',
            borderTop: '1px solid var(--tn-border)',
            display: 'flex',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '0.5rem',
            fontFamily: 'var(--font-mono)',
            fontSize: '0.72rem',
            letterSpacing: '0.03em',
            color: 'var(--tn-muted)',
          }}
        >
          <span>TREENAIL · PLANNING-SKILLS PACK</span>
          <span>craft-meets-engineering · D-011</span>
        </footer>
      </div>
    </main>
  );
}
