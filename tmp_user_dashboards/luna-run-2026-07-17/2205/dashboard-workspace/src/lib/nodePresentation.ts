type NodeAccessibleNameInput = {
  label: string;
  level?: number;
  bridge?: boolean;
  hotspotRank?: number;
};

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
}: NodeAccessibleNameInput): string {
  const details: string[] = [];
  const badgeLabel = levelBadgeLabel(level);
  if (badgeLabel) details.push(badgeLabel);
  if (bridge) details.push("bridge");
  if (hotspotRank !== undefined) details.push(`hotspot rank ${hotspotRank}`);
  return details.length > 0 ? `${label}, ${details.join(", ")}` : label;
}
