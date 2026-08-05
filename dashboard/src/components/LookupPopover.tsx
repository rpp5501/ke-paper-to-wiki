// The presentational half of select-to-look-up. Pure props in, markup out, so
// it tests under vitest's `environment: "node"`; the selectionchange wiring is
// the shell in SelectionLookup.tsx.
import type { LookupResult } from "../lib/lookup";

const KIND_LABEL = {
  glossary: "term",
  concept: "concept",
  section: "in the paper",
} as const;

export default function LookupPopover({
  onDismiss,
  onOpenConcept,
  phrase,
  result,
}: {
  onDismiss: () => void;
  /** Omitted where navigation is not available; the heading then stays plain
   *  text rather than a button that goes nowhere. */
  onOpenConcept?: (nodeId: string) => void;
  phrase: string;
  result: LookupResult | null;
}) {
  return (
    <div aria-label={`Lookup: ${phrase}`} className="lookup-popover" role="dialog">
      <button
        aria-label="Dismiss"
        className="lookup-dismiss"
        onClick={onDismiss}
        type="button"
      >
        ×
      </button>

      {result === null
        ? (
          <p className="lookup-miss">
            No entry for “{phrase}”.
          </p>
        )
        : (
          <>
            <p className="lookup-kind">{KIND_LABEL[result.kind]}</p>
            {result.kind === "glossary" && (
              <>
                <h3 className="lookup-title">{result.term}</h3>
                <p className="lookup-body">{result.definition}</p>
              </>
            )}
            {result.kind === "concept" && (
              <>
                <h3 className="lookup-title">
                  {onOpenConcept
                    ? (
                      <button
                        className="lookup-link"
                        onClick={() => onOpenConcept(result.nodeId)}
                        type="button"
                      >
                        {result.label}
                      </button>
                    )
                    : result.label}
                </h3>
                <p className="lookup-body">{result.definition}</p>
              </>
            )}
            {result.kind === "section" && (
              <>
                <h3 className="lookup-title">§{result.ref} {result.title}</h3>
                <p className="lookup-body">{result.excerpt}</p>
              </>
            )}
          </>
        )}
    </div>
  );
}
