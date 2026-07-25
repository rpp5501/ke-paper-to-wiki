// R15.11 show-source — the paper passage a node was extracted from.
// Silent when the bundle carries no sections or the ref does not resolve.
import { getSections, sectionFor } from "../lib/source";

export type SourceEntry = { ref: string; title: string; text: string };

export function SourcePanelPresentation({ entry }: { entry: SourceEntry }) {
  return (
    <details className="source-tier">
      <summary>Source: §{entry.ref} {entry.title}</summary>
      <blockquote>{entry.text}</blockquote>
    </details>
  );
}

export default function SourcePanel({
  sourceRef,
}: {
  sourceRef: string | null | undefined;
}) {
  const entry = sectionFor(sourceRef, getSections());
  return entry ? <SourcePanelPresentation entry={entry} /> : null;
}
