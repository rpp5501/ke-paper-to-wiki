// R13 — the "Visualize" drawer tier: a sandboxed, lazy-mounted explorable.
// The iframe mounts only after the tier is first opened, so unopened visuals
// cost nothing at load. sandbox="allow-scripts" (no same-origin): generated
// code stays isolated from the app.
import { useEffect, useState } from "react";

import { useApp } from "../store";
import type { VizEntry } from "../lib/viz";

export type VizTierPresentationProps = {
  entry: VizEntry;
  focused: boolean;
};

export function VizTierPresentation({
  entry,
  focused,
}: VizTierPresentationProps) {
  const [open, setOpen] = useState(focused);
  const [mounted, setMounted] = useState(focused);

  useEffect(() => {
    if (focused) {
      setOpen(true);
      setMounted(true);
    }
  }, [focused]);

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
  const setVizFocus = useApp((state) => state.setVizFocus);
  const focused = vizFocus === nodeId;

  useEffect(() => {
    if (focused) setVizFocus(null); // consume the gallery's focus request
  }, [focused, setVizFocus]);

  return <VizTierPresentation entry={entry} focused={focused} />;
}
