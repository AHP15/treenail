'use client';

import { useEffect, useRef, useState } from 'react';
import { PIPELINE } from '@/lib/pipeline-data';

// The pipeline centerpiece (D-012): the seven-skill planning pipeline as a
// scroll-linked blueprint where each joint's peg drives into place as it
// enters view. Built CSS/SVG-only — no animation library.
//
// R-006 (pointer-independent content path): every stage's reads/writes is
// real, always-in-DOM text rendered from lib/pipeline-data.ts, and each stage
// is a keyboard-focusable list item — never a hover/tap-only tooltip. Mobile,
// keyboard, and screen-reader users get the identical content.
//
// Reveal is only an enhancement: the diagram "arms" (hides stages ahead of
// their scroll reveal) ONLY after mount and ONLY when motion is allowed, so a
// no-JS render, a paused tab, or a prefers-reduced-motion user sees every
// stage fully and immediately — the static fallback carries the full text.

export function Pipeline() {
  const [armed, setArmed] = useState(false);
  const stageRefs = useRef<(HTMLLIElement | null)[]>([]);

  useEffect(() => {
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduce) return; // leave everything visible; no scroll animation

    setArmed(true);
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-in');
            observer.unobserve(entry.target);
          }
        }
      },
      { rootMargin: '0px 0px -12% 0px', threshold: 0.25 }
    );
    for (const el of stageRefs.current) if (el) observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return (
    <ol
      className={`tn-pipeline${armed ? ' tn-pipeline--armed' : ''}`}
      aria-label="The seven-skill planning pipeline, from decision to reconciled status"
    >
      {PIPELINE.map((stage, i) => (
        <li
          key={stage.skill}
          ref={(el) => {
            stageRefs.current[i] = el;
          }}
          className="tn-pipeline-stage"
          tabIndex={0}
        >
          {/* Blueprint rail: the driven peg + the connector to the next joint.
              Decorative — the meaning lives in the card text below. */}
          <div className="tn-pipeline-rail" aria-hidden="true">
            <svg className="tn-pipeline-peg" viewBox="0 0 24 24" fill="none">
              <circle
                cx="12"
                cy="12"
                r="9"
                fill="var(--tn-accent)"
                stroke="var(--tn-accent-strong)"
                strokeWidth="1.5"
              />
              <circle cx="12" cy="12" r="3.5" fill="var(--tn-accent-strong)" opacity="0.55" />
            </svg>
            {i < PIPELINE.length - 1 && <span className="tn-pipeline-connector" />}
          </div>

          <div className="tn-pipeline-card tn-panel">
            <div className="tn-pipeline-head">
              <span className="tn-pipeline-index" aria-hidden="true">
                {String(i + 1).padStart(2, '0')}
              </span>
              <code className="tn-pipeline-skill">{stage.skill}</code>
              {stage.chip && <span className="tn-id">{stage.chip}</span>}
            </div>
            <p className="tn-pipeline-summary">{stage.summary}</p>
            <dl className="tn-pipeline-io">
              <div className="tn-pipeline-io-row">
                <dt>reads</dt>
                <dd>{stage.reads}</dd>
              </div>
              <div className="tn-pipeline-io-row">
                <dt>writes</dt>
                <dd>{stage.writes}</dd>
              </div>
            </dl>
          </div>
        </li>
      ))}
    </ol>
  );
}
