import { useEffect, useId, useMemo, useState } from "react";

import { KE_DATA } from "../data.gen";
import { dependencyRings } from "../lib/deps";
import { navigationDisabledReason } from "../lib/navigation";
import { useApp, type LayoutPhase, type PlayerState } from "../store";
import type { KEEdge, KENode } from "../types";
import { useNodeNavigation } from "./useNodeNavigation";

type TourSourceStep = {
  order: number;
  nodeIds: string[];
};

const NODES = KE_DATA.nodes as KENode[];
const NODE_IDS = new Set(NODES.map((node) => node.id));
const EDGES = KE_DATA.edges as KEEdge[];
const GRAPH_KIND = (KE_DATA.meta as { kind: "concept" | "code" | "bridged" }).kind;
const TOUR = KE_DATA.tour as TourSourceStep[];
const AUTO_ADVANCE_MS = 2400;

export function readingPathSteps(
  tour: TourSourceStep[],
  availableNodeIds: Set<string>,
): string[] {
  const seen = new Set<string>();
  return [...tour]
    .sort((left, right) => left.order - right.order)
    .map((step) => step.nodeIds.find((nodeId) => availableNodeIds.has(nodeId)))
    .filter((nodeId): nodeId is string => {
      if (!nodeId || seen.has(nodeId)) return false;
      seen.add(nodeId);
      return true;
    });
}

export function blastTraceSteps(selected: string, edges: KEEdge[]): string[] {
  const dependents = [...dependencyRings(selected, edges, 3).entries()]
    .sort(([leftId, leftDepth], [rightId, rightDepth]) => (
      leftDepth - rightDepth
      || (leftId < rightId ? -1 : leftId > rightId ? 1 : 0)
    ))
    .map(([nodeId]) => nodeId);
  return [selected, ...dependents];
}

export function advancePlayback(idx: number, total: number) {
  const last = Math.max(total - 1, 0);
  const next = Math.min(idx + 1, last);
  return { idx: next, playing: next < last };
}

function usePrefersReducedMotion() {
  const [reduced, setReduced] = useState(() => (
    typeof window !== "undefined"
      && window.matchMedia("(prefers-reduced-motion: reduce)").matches
  ));

  useEffect(() => {
    const query = window.matchMedia("(prefers-reduced-motion: reduce)");
    const update = () => setReduced(query.matches);
    update();
    query.addEventListener("change", update);
    return () => query.removeEventListener("change", update);
  }, []);

  return reduced;
}

function stepDisabledReason(
  phase: LayoutPhase,
  target: string | undefined,
) {
  return navigationDisabledReason(phase, Boolean(target && NODE_IDS.has(target)));
}

function PlayerDisabledReason({ id, reason }: { id: string; reason: string | null }) {
  return reason ? <span className="sr-only" id={id}>{reason}</span> : null;
}

export function PlayerBarPresentation({
  firstStep,
  isConcept,
  layoutPhase,
  onClose,
  onMove,
  onStart,
  onTogglePlaying,
  player,
  reducedMotion,
}: {
  firstStep: string | undefined;
  isConcept: boolean;
  layoutPhase: LayoutPhase;
  onClose: () => void;
  onMove: (index: number) => void;
  onStart: () => void;
  onTogglePlaying: () => void;
  player: PlayerState;
  reducedMotion: boolean;
}) {
  const disabledReasonId = useId();

  if (!player) {
    const reason = !isConcept && !firstStep
      ? "Select a node to trace its blast radius."
      : stepDisabledReason(layoutPhase, firstStep);

    return (
      <div aria-label="Graph sequence player" className="playerbar" role="group">
        <button
          aria-describedby={reason ? disabledReasonId : undefined}
          className="pill player-idle-action"
          disabled={reason !== null}
          onClick={onStart}
          title={reason ?? undefined}
          type="button"
        >
          {isConcept ? "▶ reading path" : "▶ trace blast radius"}
        </button>
        <PlayerDisabledReason id={disabledReasonId} reason={reason} />
      </div>
    );
  }

  const previousTarget = player.steps[player.idx - 1];
  const nextTarget = player.steps[player.idx + 1];
  const previousReason = previousTarget
    ? stepDisabledReason(layoutPhase, previousTarget)
    : null;
  const nextReason = nextTarget
    ? stepDisabledReason(layoutPhase, nextTarget)
    : null;
  const playbackReason = reducedMotion
    ? "Auto-advance is unavailable when reduced motion is enabled."
    : nextTarget
      ? stepDisabledReason(layoutPhase, nextTarget)
      : null;
  const describedReason = previousReason ?? nextReason ?? playbackReason;

  return (
    <div aria-label="Graph sequence player" className="playerbar" role="group">
      <button
        aria-describedby={previousReason ? disabledReasonId : undefined}
        aria-label="Previous step"
        className="pill player-icon-action"
        disabled={!previousTarget || previousReason !== null}
        onClick={() => onMove(player.idx - 1)}
        title={previousReason ?? undefined}
        type="button"
      >
        <span aria-hidden="true">◀</span>
      </button>
      <span className="player-label">
        <strong>{player.label}</strong>
        <span>step {player.idx + 1} / {player.steps.length}</span>
      </span>
      <button
        aria-describedby={nextReason ? disabledReasonId : undefined}
        aria-label="Next step"
        className="pill player-icon-action"
        disabled={!nextTarget || nextReason !== null}
        onClick={() => onMove(player.idx + 1)}
        title={nextReason ?? undefined}
        type="button"
      >
        <span aria-hidden="true">▶</span>
      </button>
      <button
        aria-describedby={playbackReason ? disabledReasonId : undefined}
        aria-label={`${player.playing ? "Pause" : "Play"} ${player.label.toLowerCase()}`}
        className={`pill player-icon-action${player.playing ? " active" : ""}`}
        disabled={(!player.playing && !nextTarget) || playbackReason !== null}
        onClick={onTogglePlaying}
        title={playbackReason ?? undefined}
        type="button"
      >
        <span aria-hidden="true">{player.playing ? "⏸" : "▶"}</span>
      </button>
      <button
        aria-label="Close player"
        className="pill player-icon-action"
        onClick={onClose}
        type="button"
      >
        <span aria-hidden="true">×</span>
      </button>
      <p aria-atomic="true" aria-live="polite" className="sr-only" role="status">
        {player.label}, step {player.idx + 1} of {player.steps.length}.
      </p>
      <PlayerDisabledReason id={disabledReasonId} reason={describedReason} />
    </div>
  );
}

export default function PlayerBar() {
  const player = useApp((state) => state.player);
  const setPlayer = useApp((state) => state.setPlayer);
  const selected = useApp((state) => state.selected);
  const layoutPhase = useApp((state) => state.layoutPhase);
  const navigateToNode = useNodeNavigation();
  const reducedMotion = usePrefersReducedMotion();
  const readingSteps = useMemo(
    () => readingPathSteps(TOUR, NODE_IDS),
    [],
  );
  const isConcept = GRAPH_KIND === "concept";
  const firstStep = isConcept ? readingSteps[0] : selected ?? undefined;

  const start = () => {
    if (!firstStep || stepDisabledReason(layoutPhase, firstStep)) return;
    const steps = isConcept
      ? readingSteps
      : blastTraceSteps(firstStep, EDGES);
    setPlayer({
      idx: 0,
      label: isConcept ? "Reading path" : `Blast radius of ${firstStep}`,
      playing: false,
      steps,
    });
    navigateToNode(firstStep);
  };

  const moveTo = (nextIdx: number) => {
    if (!player) return;
    const bounded = Math.min(Math.max(nextIdx, 0), player.steps.length - 1);
    const nodeId = player.steps[bounded];
    if (!nodeId || stepDisabledReason(layoutPhase, nodeId)) return;
    setPlayer({ ...player, idx: bounded });
    navigateToNode(nodeId);
  };

  useEffect(() => {
    if (!player?.playing || !reducedMotion) return;
    setPlayer({ ...player, playing: false });
  }, [player, reducedMotion, setPlayer]);

  useEffect(() => {
    if (!player?.playing || reducedMotion || layoutPhase !== "ready") return;
    const timer = window.setInterval(() => {
      const current = useApp.getState().player;
      if (!current?.playing) return;
      const next = advancePlayback(current.idx, current.steps.length);
      const nodeId = current.steps[next.idx];
      setPlayer({ ...current, ...next });
      if (nodeId && next.idx !== current.idx) navigateToNode(nodeId);
    }, AUTO_ADVANCE_MS);
    return () => window.clearInterval(timer);
  }, [layoutPhase, navigateToNode, player?.playing, reducedMotion, setPlayer]);

  return (
    <PlayerBarPresentation
      firstStep={firstStep}
      isConcept={isConcept}
      layoutPhase={layoutPhase}
      onClose={() => setPlayer(null)}
      onMove={moveTo}
      onStart={start}
      onTogglePlaying={() => {
        if (player) setPlayer({ ...player, playing: !player.playing });
      }}
      player={player}
      reducedMotion={reducedMotion}
    />
  );
}
