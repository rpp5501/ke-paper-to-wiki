import { KE_DATA } from "../data.gen";
import {
  buildLearnSteps,
  type LearnStep,
  type TourSourceStep,
} from "../lib/learnPath";
import { navigationDisabledReason } from "../lib/navigation";
import { useApp, type LayoutPhase } from "../store";
import type { KENode } from "../types";
import CompactPill from "./CompactPill";
import { useNodeNavigation } from "./useNodeNavigation";

export const LEARN_STEPS: LearnStep[] = buildLearnSteps(
  KE_DATA.tour as TourSourceStep[],
  KE_DATA.nodes as KENode[],
);

const SOURCE = (KE_DATA.meta as { source?: string }).source ?? "this paper";

export function stepActivation(
  steps: LearnStep[],
  index: number,
  layoutPhase: LayoutPhase,
): { index: number; nodeId: string } | null {
  const step = steps[index];
  if (!step || navigationDisabledReason(layoutPhase, true) !== null) return null;
  return { index, nodeId: step.nodeId };
}

export function LearnPanelPresentation({
  completedSteps,
  onCloseSheet,
  onExplore,
  onStep,
  learnIdx,
}: {
  completedSteps: Set<string>;
  onCloseSheet: () => void;
  onExplore: () => void;
  onStep: (index: number) => void;
  learnIdx: number | null;
}) {
  const done = LEARN_STEPS.filter((step) => completedSteps.has(step.nodeId)).length;

  return (
    <div className="sidebar-content learn-panel">
      <div className="sidebar-sheet-header">
        <span>Learning path</span>
        <CompactPill
          aria-label="Close learning path"
          className="sidebar-sheet-close"
          onClick={onCloseSheet}
        >
          Close
        </CompactPill>
      </div>

      <header className="learn-header">
        <h2>The {LEARN_STEPS.length} ideas that matter</h2>
        <p className="learn-subtitle">
          A guided path through {SOURCE}. Plain words first, math when you're ready.
        </p>
        <p className="learn-progress" role="status">
          {done} of {LEARN_STEPS.length} visited
        </p>
      </header>

      <ol className="learn-steps">
        {LEARN_STEPS.map((step, index) => {
          const isCurrent = learnIdx === index;
          const isDone = completedSteps.has(step.nodeId);
          return (
            <li key={step.nodeId}>
              <button
                aria-current={isCurrent ? "step" : undefined}
                aria-label={`Step ${index + 1}: ${step.title}`}
                className={`learn-step${isCurrent ? " is-current" : ""}${isDone ? " is-done" : ""}`}
                onClick={() => onStep(index)}
                type="button"
              >
                <span aria-hidden="true" className="learn-step-marker">
                  {isDone && !isCurrent ? "✓" : index + 1}
                </span>
                <span className="learn-step-body">
                  <strong>{step.title}</strong>
                  <span className="learn-step-blurb">{step.blurb}</span>
                </span>
              </button>
            </li>
          );
        })}
      </ol>

      <button
        className="learn-explore-link"
        onClick={onExplore}
        type="button"
      >
        Show the full map ({(KE_DATA.nodes as KENode[]).length} concepts) →
      </button>
    </div>
  );
}

export function switchToExplore() {
  useApp.getState().setMode("explore");
}

export default function LearnPanel({ onCloseSheet }: { onCloseSheet: () => void }) {
  const { learnIdx, setLearnIdx, completedSteps, layoutPhase } = useApp();
  const navigateToNode = useNodeNavigation();

  const goTo = (index: number) => {
    const target = stepActivation(LEARN_STEPS, index, layoutPhase);
    if (!target) return;
    setLearnIdx(target.index);
    navigateToNode(target.nodeId);
  };

  return (
    <LearnPanelPresentation
      completedSteps={completedSteps}
      onCloseSheet={onCloseSheet}
      onExplore={switchToExplore}
      onStep={goTo}
      learnIdx={learnIdx}
    />
  );
}
