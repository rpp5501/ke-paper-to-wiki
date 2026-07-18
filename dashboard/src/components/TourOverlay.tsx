import { useEffect, useId, useMemo } from "react";

import { KE_DATA } from "../data.gen";
import type { TourSourceStep } from "../lib/learnPath";
import { navigationDisabledReason } from "../lib/navigation";
import { useApp } from "../store";
import type { KENode } from "../types";
import { useNodeNavigation } from "./useNodeNavigation";

export type { TourSourceStep };

export type TourStep = Omit<TourSourceStep, "nodeIds"> & { nodeId: string };

const NODES = KE_DATA.nodes as KENode[];
const NODE_IDS = new Set(NODES.map((node) => node.id));
const TOUR = KE_DATA.tour as TourSourceStep[];

export function hasNavigableTourStep(
  tour: Pick<TourSourceStep, "nodeIds">[],
  availableNodeIds: Set<string>,
) {
  return tour.some((step) => (
    step.nodeIds.some((nodeId) => availableNodeIds.has(nodeId))
  ));
}

export function orderedTourSteps(
  tour: TourSourceStep[],
  availableNodeIds: Set<string>,
): TourStep[] {
  return [...tour]
    .sort((left, right) => left.order - right.order)
    .flatMap((step) => {
      const nodeId = step.nodeIds.find((candidate) => availableNodeIds.has(candidate));
      return nodeId
        ? [{
          order: step.order,
          title: step.title,
          description: step.description,
          nodeId,
        }]
        : [];
    });
}

export function isTourDismissKey(key: string) {
  return key === "Escape";
}

export function TourOverlayPresentation({
  dismissed,
  layoutPhase,
  onDismiss,
  onGo,
  steps,
  tourIdx,
}: {
  dismissed: boolean;
  layoutPhase: "loading" | "ready" | "empty" | "error";
  onDismiss: () => void;
  onGo: (index: number) => void;
  steps: TourStep[];
  tourIdx: number | null;
}) {
  const reasonId = useId();

  if (dismissed || steps.length === 0) return null;

  const boundedIdx = tourIdx === null
    ? null
    : Math.min(Math.max(tourIdx, 0), steps.length - 1);
  const active = boundedIdx === null ? null : steps[boundedIdx];
  const targetReason = active
    ? navigationDisabledReason(layoutPhase, NODE_IDS.has(active.nodeId))
    : navigationDisabledReason(layoutPhase, Boolean(steps[0]?.nodeId));
  const go = (index: number) => {
    const step = steps[index];
    if (!step || navigationDisabledReason(layoutPhase, NODE_IDS.has(step.nodeId))) return;
    onGo(index);
  };

  return (
    <section aria-label="Guided tour" className="tour-overlay">
      <div className="tour-heading">
        <h3>{active?.title ?? "Guided tour"}</h3>
        <button
          aria-label="Dismiss guided tour"
          className="tour-dismiss"
          onClick={onDismiss}
          type="button"
        >
          <span aria-hidden="true">×</span>
        </button>
      </div>
      {active ? (
        <>
          <p className="tour-description">{active.description}</p>
          <div className="tour-actions">
            <button
              aria-describedby={targetReason ? reasonId : undefined}
              className="pill tour-action"
              disabled={boundedIdx === 0 || targetReason !== null}
              onClick={() => go((boundedIdx ?? 0) - 1)}
              title={targetReason ?? undefined}
              type="button"
            >
              Back
            </button>
            <span className="tour-progress">{(boundedIdx ?? 0) + 1}/{steps.length}</span>
            {(boundedIdx ?? 0) < steps.length - 1 ? (
              <button
                aria-describedby={targetReason ? reasonId : undefined}
                className="pill tour-action active"
                disabled={targetReason !== null}
                onClick={() => go((boundedIdx ?? 0) + 1)}
                title={targetReason ?? undefined}
                type="button"
              >
                Next
              </button>
            ) : (
              <button
                className="pill tour-action"
                onClick={onDismiss}
                type="button"
              >
                Finish
              </button>
            )}
          </div>
          <p aria-atomic="true" aria-live="polite" className="sr-only" role="status">
            Tour step {(boundedIdx ?? 0) + 1} of {steps.length}: {active.title}.
          </p>
        </>
      ) : (
        <>
          <p className="tour-description">Walk the {steps.length} key concepts.</p>
          <button
            aria-describedby={targetReason ? reasonId : undefined}
            className="pill tour-action active"
            disabled={targetReason !== null}
            onClick={() => go(0)}
            title={targetReason ?? undefined}
            type="button"
          >
            Start
          </button>
        </>
      )}
      {targetReason && <span className="sr-only" id={reasonId}>{targetReason}</span>}
    </section>
  );
}

export default function TourOverlay({
  escapeEnabled = true,
}: {
  escapeEnabled?: boolean;
}) {
  const tourIdx = useApp((state) => state.tourIdx);
  const setTourIdx = useApp((state) => state.setTourIdx);
  const dismissed = useApp((state) => state.tourDismissed);
  const dismissTour = useApp((state) => state.dismissTour);
  const layoutPhase = useApp((state) => state.layoutPhase);
  const navigateToNode = useNodeNavigation();
  const steps = useMemo(() => orderedTourSteps(TOUR, NODE_IDS), []);

  useEffect(() => {
    if (!escapeEnabled || dismissed || steps.length === 0) return;
    const onKeyDown = (event: globalThis.KeyboardEvent) => {
      if (!isTourDismissKey(event.key)) return;
      event.stopImmediatePropagation();
      dismissTour();
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [dismissTour, dismissed, escapeEnabled, steps.length]);

  return (
    <TourOverlayPresentation
      dismissed={dismissed}
      layoutPhase={layoutPhase}
      onDismiss={dismissTour}
      onGo={(index) => {
        const step = steps[index];
        if (!step) return;
        setTourIdx(index);
        navigateToNode(step.nodeId);
      }}
      steps={steps}
      tourIdx={tourIdx}
    />
  );
}
