export function ghostStyles(
  rings: Map<string, number>,
  allIds: string[],
  selected?: string,
): Map<string, { opacity: number; ring: number }> {
  const out = new Map<string, { opacity: number; ring: number }>();
  for (const id of allIds) {
    if (id === selected) out.set(id, { opacity: 1, ring: 0 });
    else if (rings.has(id)) out.set(id, { opacity: 1, ring: rings.get(id)! });
    else out.set(id, { opacity: 0.1, ring: -1 });
  }
  return out;
}
