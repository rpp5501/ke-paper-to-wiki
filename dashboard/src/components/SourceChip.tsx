// R16.C2 — the provenance chip. Every quiz item and every visual that claims
// a paper span shows where it came from; clicking opens that node's source.
// Silent when the ref does not resolve, so a chip never goes nowhere — the
// build drops unresolvable refs, and this is the second line of defence.
import { getSections, sectionFor, type SourceSection } from "../lib/source";

export default function SourceChip({
  onOpen,
  sections = getSections(),
  sourceRef,
}: {
  /** Omit where the source is already on screen — a button that navigates
   *  nowhere is worse than a plain label. */
  onOpen?: () => void;
  sections?: Record<string, SourceSection>;
  sourceRef: string | null | undefined;
}) {
  const entry = sectionFor(sourceRef, sections);
  if (!entry) return null;

  const label = (
    <>
      §{entry.ref}
      <span className="sr-only"> {entry.title}</span>
    </>
  );

  return onOpen
    ? (
      <button
        className="source-chip"
        onClick={onOpen}
        title={entry.title}
        type="button"
      >
        {label}
      </button>
    )
    : <span className="source-chip" title={entry.title}>{label}</span>;
}
