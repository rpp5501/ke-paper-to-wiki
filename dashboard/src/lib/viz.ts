// R13 visualize feature — typed access to the optional KE_DATA.viz map.
// A viz-free build has no `viz` key; every consumer must go through here.
import { KE_DATA } from "../data.gen";

export type VizEntry = {
  kind: string;
  templateId?: string | null;
  title: string;
  caption: string;
  prompt: string;
  srcdoc: string;
  stale: boolean;
  /** R16.C2 — the paper span this visual was built from, when it cites one. */
  sectionRef?: string;
  /** R13.1 — where the skill placed this visual on the page. */
  anchorTier?: string;
};

// R13.1 — the manifest's placement vocabulary mapped onto page tier ids. An
// unrecognised placement falls back to Intuition rather than dropping the
// visual: a hand-edited manifest must not make it vanish.
export function vizAnchorTier(entry: { anchorTier?: string } | undefined): string {
  return entry?.anchorTier === "in-the-math" ? "the-math" : "intuition";
}

export function vizMapFrom(data: unknown): Record<string, VizEntry> {
  const viz = (data as { viz?: Record<string, VizEntry> }).viz;
  return viz ?? {};
}

const VIZ = vizMapFrom(KE_DATA);

export function getVizMap(): Record<string, VizEntry> {
  return VIZ;
}

export function getViz(nodeId: string | null): VizEntry | undefined {
  return nodeId ? VIZ[nodeId] : undefined;
}
