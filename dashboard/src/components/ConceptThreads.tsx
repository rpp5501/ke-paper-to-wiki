/** One end of a dependency: the concept, and where to read it. */
export type Thread = { id: string; label: string };
export type ConceptThreadSet = { buildsOn: Thread[]; setsUp: Thread[] };

/**
 * Why this concept exists given what came before, and what it unlocks.
 *
 * Derived from the graph's builds-on and prerequisite edges rather than
 * written, so it cannot drift from the concept map. A paper is a dependency
 * graph and its prose can only be read in one order; this is the part the
 * reader otherwise has to reconstruct by reading everything.
 *
 * Renders nothing when a concept has no threads — roughly half of them are
 * joined only by part-of, and an empty heading on every one of those pages is
 * noise rather than information.
 */
export default function ConceptThreads({
  reachable,
  threads,
}: {
  /** Ids that have an anchor on this page. Omit to link everything. */
  reachable?: Set<string>;
  threads?: ConceptThreadSet;
}) {
  const buildsOn = threads?.buildsOn ?? [];
  const setsUp = threads?.setsUp ?? [];
  if (!buildsOn.length && !setsUp.length) return null;

  return (
    <aside aria-label="How this connects" className="concept-threads">
      {buildsOn.length > 0 && (
        <ThreadRow
          arrow="←"
          label="Builds on"
          reachable={reachable}
          threads={buildsOn}
        />
      )}
      {setsUp.length > 0 && (
        <ThreadRow
          arrow="→"
          label="Sets up"
          reachable={reachable}
          threads={setsUp}
        />
      )}
    </aside>
  );
}

function ThreadRow({
  arrow,
  label,
  reachable,
  threads,
}: {
  arrow: string;
  label: string;
  reachable?: Set<string>;
  threads: Thread[];
}) {
  return (
    <p className="concept-thread-row">
      <span aria-hidden="true" className="concept-thread-arrow">
        {arrow}
      </span>
      <span className="concept-thread-label">{label}</span>
      <span className="concept-thread-links">
        {threads.map((thread, i) => (
          <span key={thread.id}>
            {i > 0 && <span aria-hidden="true">, </span>}
            {/* A link that scrolls nowhere teaches the reader the
                navigation is broken; the thread is still worth naming. */}
            {!reachable || reachable.has(thread.id) ? (
              <a href={`#${thread.id}`}>{thread.label}</a>
            ) : (
              <span className="concept-thread-offpath">{thread.label}</span>
            )}
          </span>
        ))}
      </span>
    </p>
  );
}
