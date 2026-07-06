import Link from 'next/link';
import { ThemeToggle } from './components/theme-toggle';
import { JointDiagram } from './components/joint-diagram';
import { Pipeline } from './components/pipeline';
import { CopyCommand } from './components/copy-command';
import { NewsletterForm } from './components/newsletter-form';

// The landing page: eight-section, pain-led narrative arc (D-009), aimed at
// the individual developer using an AI coding agent (D-008). Section 4 hosts
// the animated pipeline centerpiece (T-008). Agent-tier + quickstart copy is
// provisional here and gated for accuracy pre-launch by T-018 — the tiers are
// phrased to convey honest degradation, never parity.

const GITHUB_URL = 'https://github.com/AHP15/treenail';

const PROBLEMS = [
  {
    title: 'It drifts',
    body: 'Twenty messages in, the agent has quietly wandered off the plan and is solving a problem you never had.',
  },
  {
    title: 'It forgets why',
    body: 'The reason a choice was made evaporates from the context window, so settled questions get silently reopened.',
  },
  {
    title: 'You re-litigate',
    body: 'Every session re-argues the same trade-offs from scratch because nothing durable recorded the last verdict.',
  },
];

const TIERS = [
  {
    agent: 'Claude Code',
    badge: 'Full support',
    full: true,
    body: 'The interactive pipeline is built and tested against Claude Code first — skills, plugin install, and the shared runtime.',
  },
  {
    agent: 'Codex',
    badge: 'Partial',
    full: false,
    body: 'Installs and runs, with a more limited interactive experience. Expect rougher edges around the conversational skills.',
  },
  {
    agent: 'opencode',
    badge: 'Partial',
    full: false,
    body: 'Supported on a best-effort basis; the richer interactive flows degrade. Use the record files as the source of truth.',
  },
];

export default function HomePage() {
  return (
    <main className="tn-blueprint-grid">
      <div className="tn-shell">
        {/* --- Header --- */}
        <header
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '1rem',
            paddingBlock: '1.5rem',
          }}
        >
          <span className="tn-brand">
            <span className="tn-brand-peg" aria-hidden />
            Treenail
          </span>
          <nav className="tn-nav">
            <Link href="/docs" style={{ color: 'var(--tn-muted)' }}>
              Docs
            </Link>
            <a href={GITHUB_URL} style={{ color: 'var(--tn-muted)' }} rel="noreferrer">
              GitHub
            </a>
            <Link href="/contact" style={{ color: 'var(--tn-muted)' }}>
              Contact
            </Link>
            <ThemeToggle />
          </nav>
        </header>

        {/* --- 1. Hero: lead with the pain (D-008) --- */}
        <section
          className="tn-rise"
          style={{
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
              Stop your coding agent losing the plot.
            </h1>
            <p className="tn-lead">
              Treenail is a durable planning spine for your AI coding agent. It
              keeps decisions, risks, and tasks as a versioned record pegged into
              your repo — so the plan survives the context window, and drift,
              forgetting, and re-litigation end.
            </p>

            <div style={{ marginTop: '2rem', maxWidth: '30rem' }}>
              <CopyCommand command="npx treenail install" label="Copy the install command" />
            </div>

            <div
              style={{
                marginTop: '1.5rem',
                display: 'flex',
                gap: '0.85rem',
                flexWrap: 'wrap',
              }}
            >
              <Link href="/docs" className="tn-btn tn-btn--accent">
                Read the docs
              </Link>
              <a href={GITHUB_URL} className="tn-btn" rel="noreferrer">
                View on GitHub
              </a>
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

        {/* --- 2. The problem --- */}
        <section className="tn-section">
          <p className="tn-eyebrow">01 · The problem</p>
          <h2 className="tn-h2">Agents are brilliant in the moment and amnesiac across it.</h2>
          <p className="tn-lead">
            The failure isn&rsquo;t intelligence — it&rsquo;s memory. Everything
            that matters lives in a chat log that scrolls away.
          </p>
          <div className="tn-grid-3">
            {PROBLEMS.map((p) => (
              <div key={p.title} className="tn-panel tn-card">
                <h3>{p.title}</h3>
                <p>{p.body}</p>
              </div>
            ))}
          </div>
        </section>

        {/* --- 3. The core idea --- */}
        <section className="tn-section">
          <p className="tn-eyebrow">02 · The idea</p>
          <h2 className="tn-h2">A planning spine that lives in your repo, not the chat.</h2>
          <p className="tn-lead">
            Treenail records every <span className="tn-id">D-NNN</span> decision,{' '}
            <span className="tn-id">R-NNN</span> risk, and{' '}
            <span className="tn-id">T-NNN</span> task as a plain-text file, versioned
            alongside your code. The agent reads and writes that record through a
            small pipeline of skills — so the plan is a durable artifact you own,
            reviewable in a diff, and never trapped in a context window again.
          </p>
        </section>

        {/* --- 4. The pipeline: animated centerpiece (T-008) --- */}
        <section className="tn-section">
          <p className="tn-eyebrow">03 · The pipeline</p>
          <h2 className="tn-h2">Seven skills, one durable joint.</h2>
          <p className="tn-lead">
            Each skill reads the records the last one wrote and drives the next
            peg into place — from the first interrogation of your plan to the
            reconciled status of what actually shipped.
          </p>
          <div style={{ marginTop: 'clamp(1.75rem, 4vw, 2.75rem)', maxWidth: '46rem' }}>
            <Pipeline />
          </div>
        </section>

        {/* --- 5. Why it stays fast --- */}
        <section className="tn-section">
          <p className="tn-eyebrow">04 · Performance</p>
          <h2 className="tn-h2">
            It reads <span className="tn-id">O(active work)</span>, not O(everything).
          </h2>
          <p className="tn-lead">
            The record is indexed so the agent only ever loads the decisions,
            risks, and tasks that are in play — terminal records are archived out
            of the active read path. The plan can grow for months without the
            context cost growing with it.
          </p>
        </section>

        {/* --- 6. Supported agents: honest tiers (gated by T-018) --- */}
        <section className="tn-section">
          <p className="tn-eyebrow">05 · Supported agents</p>
          <h2 className="tn-h2">Honest about where it shines.</h2>
          <p className="tn-lead">
            Treenail installs for the AI coding agents you already use. Support is
            deepest where it&rsquo;s been proven — and we say so plainly.
          </p>
          <div className="tn-grid-3">
            {TIERS.map((t) => (
              <div key={t.agent} className="tn-panel tn-card tn-tier">
                <span className={`tn-tier-badge${t.full ? ' tn-tier-badge--full' : ''}`}>
                  {t.badge}
                </span>
                <h3>{t.agent}</h3>
                <p>{t.body}</p>
              </div>
            ))}
          </div>
        </section>

        {/* --- 7. Quickstart --- */}
        <section className="tn-section">
          <p className="tn-eyebrow">06 · Quickstart</p>
          <h2 className="tn-h2">Three commands to a planning spine.</h2>
          <p className="tn-lead">
            Requires Node&nbsp;≥&nbsp;22. The installer detects which supported
            agents are present and installs only for those — then restart your
            agent.
          </p>
          <div
            style={{
              marginTop: 'clamp(1.5rem, 4vw, 2.25rem)',
              display: 'flex',
              flexDirection: 'column',
              gap: '0.75rem',
              maxWidth: '32rem',
            }}
          >
            <CopyCommand command="npx treenail detect" />
            <CopyCommand command="npx treenail install" />
            <CopyCommand command="npx treenail update" />
          </div>
        </section>

        {/* --- 8. Newsletter + contact CTA --- */}
        <section className="tn-section">
          <p className="tn-eyebrow">07 · Stay in the loop</p>
          <h2 className="tn-h2">Occasional updates. No spam.</h2>
          <p className="tn-lead">
            Get notified about releases and new agent support. Or reach out
            directly — we read every message.
          </p>
          <div style={{ marginTop: '1.5rem', maxWidth: '32rem' }}>
            <NewsletterForm />
          </div>
          <p style={{ marginTop: '1.5rem' }}>
            <Link href="/contact" className="tn-btn">
              Get in touch
            </Link>
          </p>
        </section>

        {/* --- Footer --- */}
        <footer
          style={{
            paddingBlock: '1.5rem',
            marginTop: 'clamp(2rem, 6vw, 4rem)',
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
