import type { MasteryLevel } from "./mastery";

type NodeAccessibleNameInput = {
  label: string;
  level?: number;
  bridge?: boolean;
  hotspotRank?: number;
  mastery?: MasteryLevel;
  hidden?: number;
};

// R16.A2 — mastery is evidence, not a score, so it reads as a plain state.
// "unseen" is the default for most of the graph; announcing it on every node
// would be noise, so it stays silent.
export function masteryNote(level: MasteryLevel | undefined): string | null {
  return !level || level === "unseen" ? null : level;
}

export function levelBadgeLabel(level: number | undefined): string | null {
  if (level === undefined) return null;
  if (level <= 1) return "core idea";
  if (level === 2) return "mechanism";
  return "deep dive";
}

export function nodeAccessibleName({
  label,
  level,
  bridge,
  hotspotRank,
  mastery,
  hidden,
}: NodeAccessibleNameInput): string {
  const details: string[] = [];
  const badgeLabel = levelBadgeLabel(level);
  if (badgeLabel) details.push(badgeLabel);
  if (bridge) details.push("bridge");
  if (hotspotRank !== undefined) details.push(`hotspot rank ${hotspotRank}`);
  const note = masteryNote(mastery);
  if (note) details.push(note);
  if (hidden !== undefined && hidden > 0) {
    details.push(`collapsed, ${hidden} hidden`);
  }
  return details.length > 0 ? `${label}, ${details.join(", ")}` : label;
}
