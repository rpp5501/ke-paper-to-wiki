import { useApp } from "../store";
import type { Chapter } from "../lib/article";
import { masteryNote } from "../lib/nodePresentation";
import { recordFor, type MasteryLedger } from "../lib/mastery";
import { switchToExplore } from "./LearnPanel";

export function ProgressRailPresentation({
  chapters,
  completedSteps,
  hasClosing,
  hasNotation,
  learnIdx,
  mastery,
  onExplore,
  onJump,
}: {
  chapters: Chapter[];
  completedSteps: Set<string>;
  hasClosing: boolean;
  hasNotation: boolean;
  learnIdx: number | null;
  mastery: MasteryLedger;
  onExplore: () => void;
  onJump: (anchor: string) => void;
}) {
  const done = chapters.filter((chapter) => completedSteps.has(chapter.nodeId)).length;

  return (
    <nav aria-label="Reading progress" className="progress-rail">
      <p className="rail-progress" role="status">
        {done} of {chapters.length} read
      </p>
      <ol className="rail-chapters">
        {chapters.map((chapter, index) => {
          const isCurrent = learnIdx === index;
          const isDone = completedSteps.has(chapter.nodeId);
          const level = recordFor(mastery, chapter.nodeId).level;
          const note = masteryNote(level);
          return (
            <li key={chapter.nodeId}>
              <button
                aria-current={isCurrent ? "step" : undefined}
                className={`rail-chapter${isCurrent ? " is-current" : ""}${isDone ? " is-done" : ""}`}
                onClick={() => onJump(chapter.nodeId)}
                type="button"
              >
                <span
                  aria-hidden="true"
                  className="rail-marker"
                  data-mastery={note ?? undefined}
                >
                  {isDone && !isCurrent ? "✓" : index + 1}
                </span>
                <span className="rail-title">{chapter.title}</span>
                {note && <span className="sr-only">{note}</span>}
              </button>
            </li>
          );
        })}
      </ol>
      {hasNotation && (
        <button
          className="rail-link"
          onClick={() => onJump("notation")}
          type="button"
        >
          Notation guide
        </button>
      )}
      {hasClosing && (
        <button
          className="rail-link"
          onClick={() => onJump("closing")}
          type="button"
        >
          You can now…
        </button>
      )}
      <button className="rail-explore" onClick={onExplore} type="button">
        Full concept map →
      </button>
    </nav>
  );
}

export default function ProgressRail({
  chapters,
  hasClosing,
  hasNotation,
  onJump,
}: {
  chapters: Chapter[];
  hasClosing: boolean;
  hasNotation: boolean;
  onJump: (anchor: string) => void;
}) {
  const learnIdx = useApp((state) => state.learnIdx);
  const completedSteps = useApp((state) => state.completedSteps);
  const mastery = useApp((state) => state.mastery);

  return (
    <ProgressRailPresentation
      chapters={chapters}
      completedSteps={completedSteps}
      hasClosing={hasClosing}
      hasNotation={hasNotation}
      learnIdx={learnIdx}
      mastery={mastery}
      onExplore={switchToExplore}
      onJump={onJump}
    />
  );
}
