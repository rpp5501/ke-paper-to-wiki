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
};

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
