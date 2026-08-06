import { useApp } from "../store";
import type { Chapter } from "../lib/article";
import { masteryNote } from "../lib/nodePresentation";
import {
  higherLevel,
  recordFor,
  type MasteryLedger,
  type MasteryLevel,
} from "../lib/mastery";
import { switchToExplore } from "./LearnPanel";

function chapterLevel(chapter: Chapter, mastery: MasteryLedger): MasteryLevel {
  const sections = chapter.sections ?? [];
  const nodeIds = sections.length > 0
    ? sections.map((section) => section.nodeId)
    : [chapter.nodeId];
  return nodeIds.reduce<MasteryLevel>(
    (level, nodeId) => higherLevel(level, recordFor(mastery, nodeId).level),
    "unseen",
  );
}

function progressStatus(
  current: boolean,
  read: boolean,
  level: MasteryLevel,
) {
  if (level === "mastered") return "Mastered";
  if (level === "practiced") return "Practiced";
  if (read || level === "read") return "Read";
  if (current || level === "reading") return "Reading";
  return "Not started";
}

export function ProgressRailPresentation({
  chapters,
  completedSteps,
  hasClosing,
  hasNotation,
  learnIdx,
  mastery,
  onExplore,
  onClose,
  onJump,
}: {
  chapters: Chapter[];
  completedSteps: Set<string>;
  hasClosing: boolean;
  hasNotation: boolean;
  learnIdx: number | null;
  mastery: MasteryLedger;
  onExplore: () => void;
  onClose?: () => void;
  onJump: (anchor: string) => void;
}) {
  const done = chapters.filter((chapter) => (
    completedSteps.has(chapter.nodeId) || recordFor(mastery, chapter.nodeId).read
  )).length;

  return (
    <nav aria-label="Reading progress" className="progress-rail">
      {onClose && (
        <button
          aria-label="Hide reading progress"
          className="rail-close"
          onClick={onClose}
          type="button"
        >
          ×
        </button>
      )}
      <p className="rail-progress" role="status">
        {done} of {chapters.length} read
      </p>
      <ol className="rail-chapters">
        {chapters.map((chapter, index) => {
          const isCurrent = learnIdx === index;
          const isDone = completedSteps.has(chapter.nodeId)
            || recordFor(mastery, chapter.nodeId).read;
          const level = chapterLevel(chapter, mastery);
          const note = masteryNote(level);
          const status = progressStatus(isCurrent, isDone, level);
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
                <span className="rail-copy">
                  <span className="rail-title">{chapter.title}</span>
                  <span className="rail-status">{status}</span>
                </span>
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
  onClose,
}: {
  chapters: Chapter[];
  hasClosing: boolean;
  hasNotation: boolean;
  onJump: (anchor: string) => void;
  onClose?: () => void;
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
      onClose={onClose}
      onJump={onJump}
    />
  );
}
