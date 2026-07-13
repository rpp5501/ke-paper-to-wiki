type NodeAccessibleNameInput = {
  label: string;
  level?: number;
  bridge?: boolean;
  hotspotRank?: number;
};

export function nodeAccessibleName({
  label,
  level,
  bridge,
  hotspotRank,
}: NodeAccessibleNameInput): string {
  const details: string[] = [];
  if (level !== undefined) details.push(`level ${level}`);
  if (bridge) details.push("bridge");
  if (hotspotRank !== undefined) details.push(`hotspot rank ${hotspotRank}`);
  return details.length > 0 ? `${label}, ${details.join(", ")}` : label;
}
