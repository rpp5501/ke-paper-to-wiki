/** How much of the selection the chip shows before it would start to sprawl. */
const MAX_CHARS = 28;

/**
 * The offer, not the answer.
 *
 * A popover that opens by itself interrupts whatever the reader was doing —
 * copying a sentence, dragging across a heading. This asks first, and costs
 * one click to ignore.
 */
export default function LookupChip({
  onOpen,
  phrase,
}: {
  onOpen: () => void;
  phrase: string;
}) {
  const shown = phrase.length > MAX_CHARS
    ? `${phrase.slice(0, MAX_CHARS - 1).trimEnd()}…`
    : phrase;

  return (
    <button
      className="lookup-chip"
      onClick={onOpen}
      title={`Look up “${phrase}”`}
      type="button"
    >
      <span aria-hidden="true" className="lookup-chip-icon">⌕</span>
      <span className="lookup-chip-text">Look up “{shown}”</span>
    </button>
  );
}
