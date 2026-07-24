// R13 — the "Visualize" drawer tier: a sandboxed, lazy-mounted explorable.
// The iframe mounts only after the tier is first opened, so unopened visuals
// cost nothing at load. sandbox="allow-scripts" (no same-origin): generated
// code stays isolated from the app.
import { useCallback, useEffect, useRef, useState } from "react";

import { useApp } from "../store";
import type { VizEntry } from "../lib/viz";

// R16.A1 — validate a bet payload from generated template code. Returns the
// outcome, or null for anything that is not a well-formed bet message.
// Exported so the parsing rules are unit-testable without a DOM.
export function betOutcome(data: unknown): boolean | null {
  if (!data || typeof data !== "object") return null;

  const message = data as { type?: unknown; correct?: unknown };
  if (message.type !== "ke-bet-resolved") return null;
  if (typeof message.correct !== "boolean") return null;

  return message.correct;
}

export type VizTierPresentationProps = {
  entry: VizEntry;
  focused: boolean;
  onBetResolved?: (correct: boolean) => void;
};

export function VizTierPresentation({
  entry,
  focused,
  onBetResolved,
}: VizTierPresentationProps) {
  const [open, setOpen] = useState(focused);
  const [mounted, setMounted] = useState(focused);
  const frameRef = useRef<HTMLIFrameElement | null>(null);

  useEffect(() => {
    if (focused) {
      setOpen(true);
      setMounted(true);
    }
  }, [focused]);

  // R16.A1 — templates report a resolved predict-then-reveal bet, which feeds
  // the same mastery ledger the quiz does. The frame is sandboxed without
  // allow-same-origin, so its origin is the opaque string "null" and proves
  // nothing; identify the sender by window identity instead. Any node id the
  // frame claims is ignored — this tier already knows which node it renders,
  // and generated code must not be able to mark other nodes mastered.
  useEffect(() => {
    if (!mounted || !onBetResolved) return;

    const onMessage = (event: MessageEvent) => {
      if (!frameRef.current) return;
      if (event.source !== frameRef.current.contentWindow) return;

      const correct = betOutcome(event.data);
      if (correct === null) return;

      onBetResolved(correct);
    };

    window.addEventListener("message", onMessage);
    return () => window.removeEventListener("message", onMessage);
  }, [mounted, onBetResolved]);

  return (
    <details
      className="viz-tier"
      onToggle={(event) => {
        const isOpen = (event.target as HTMLDetailsElement).open;
        setOpen(isOpen);
        if (isOpen) setMounted(true);
      }}
      open={open}
    >
      <summary>Visualize</summary>
      <div className="tier-body">
        {entry.stale && (
          <p className="viz-stale" role="status">
            This visual was built from an older version of the page — values
            may not match the text.
          </p>
        )}
        {mounted && (
          <iframe
            className="viz-frame"
            ref={frameRef}
            sandbox="allow-scripts"
            srcDoc={entry.srcdoc}
            title={entry.title}
          />
        )}
        <p className="viz-caption">{entry.caption}</p>
      </div>
    </details>
  );
}

type VizTierProps = {
  nodeId: string;
  entry: VizEntry;
};

export default function VizTier({ nodeId, entry }: VizTierProps) {
  const vizFocus = useApp((state) => state.vizFocus);
  const recordMastery = useApp((state) => state.recordMastery);
  const focused = vizFocus === nodeId;

  const onBetResolved = useCallback(
    (correct: boolean) => recordMastery(nodeId, correct),
    [nodeId, recordMastery],
  );

  return (
    <VizTierPresentation
      entry={entry}
      focused={focused}
      onBetResolved={onBetResolved}
    />
  );
}
