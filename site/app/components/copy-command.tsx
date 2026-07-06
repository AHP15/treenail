'use client';

import { useState } from 'react';

// A shell command with a tasteful copy affordance (D-012 micro-interactions).
// The command text is always selectable; the button is progressive
// enhancement — it works without JS as plain, readable text.
export function CopyCommand({ command, label }: { command: string; label?: string }) {
  const [copied, setCopied] = useState(false);

  async function copy() {
    try {
      await navigator.clipboard.writeText(command);
      setCopied(true);
      setTimeout(() => setCopied(false), 1600);
    } catch {
      /* clipboard unavailable — the text stays selectable */
    }
  }

  return (
    <div className="tn-cmd tn-panel">
      <span className="tn-cmd-prompt" aria-hidden="true">
        $
      </span>
      <code className="tn-cmd-text">{command}</code>
      <button
        type="button"
        className="tn-cmd-copy"
        onClick={copy}
        aria-label={copied ? 'Copied' : label ?? `Copy: ${command}`}
      >
        {copied ? 'copied' : 'copy'}
      </button>
    </div>
  );
}
