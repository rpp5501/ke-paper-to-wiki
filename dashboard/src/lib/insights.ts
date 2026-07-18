import type { Insight, KEEdge, KENode } from "../types";
import {
  normalizeDependencies,
  type NormalizedDependency,
} from "./deps";

const DEAD_CODE_KINDS = new Set(["function", "class", "file"]);
const ENTRY_NAMES = new Set(["main", "__main__"]);

function isEntryNode(node: KENode): boolean {
  return [node.id, node.label].some((value) => {
    const normalized = value.trim().toLowerCase();
    const symbol = normalized.split("::").at(-1) ?? normalized;
    return ENTRY_NAMES.has(symbol);
  });
}

function findCycle(
  nodes: KENode[],
  relations: NormalizedDependency[],
): string[] | null {
  const adj = new Map<string, string[]>();
  for (const { dependent, dependency } of relations) {
    const outgoing = adj.get(dependency) ?? [];
    outgoing.push(dependent);
    adj.set(dependency, outgoing);
  }
  const state = new Map<string, 1 | 2>();
  const stack: string[] = [];
  const visit = (v: string): string[] | null => {
    state.set(v, 1);
    stack.push(v);
    for (const w of adj.get(v) ?? []) {
      if (state.get(w) === 1) return stack.slice(stack.indexOf(w));
      if (!state.has(w)) {
        const cycle = visit(w);
        if (cycle) return cycle;
      }
    }
    stack.pop();
    state.set(v, 2);
    return null;
  };
  for (const n of nodes) {
    if (!state.has(n.id)) {
      const cycle = visit(n.id);
      if (cycle) return cycle;
    }
  }
  return null;
}

export function computeInsights(data: {
  nodes: KENode[];
  edges: KEEdge[];
  notes: Record<string, { status?: string; unresolved?: string[]; date?: string }>;
  mtimes?: Record<string, string>;
  provenance: { equation_fidelity?: string };
  centrality: Record<string, number>;
  meta: { kind?: string };
}): Insight[] {
  const out: Insight[] = [];
  const relations = normalizeDependencies(data.edges);
  const hasDependents = new Set(relations.map(({ dependency }) => dependency));

  for (const n of data.nodes) {
    if (
      DEAD_CODE_KINDS.has(n.kind)
      && !isEntryNode(n)
      && !hasDependents.has(n.id)
    ) {
      out.push({
        severity: "MED",
        rule: "dead-code",
        nodeId: n.id,
        text: `${n.label}: nothing depends on it — potentially dead`,
      });
    }
  }

  for (const [id, modified] of Object.entries(data.mtimes ?? {})) {
    const noteDate = data.notes[id]?.date;
    if (noteDate && modified > noteDate) {
      out.push({
        severity: "HIGH",
        rule: "stale-doc",
        nodeId: id,
        text: `code edited ${modified}, doc last updated ${noteDate} — drift`,
      });
    }
  }

  const cycle = findCycle(data.nodes, relations);
  if (cycle) {
    out.push({
      severity: "MED",
      rule: "cycle",
      nodeId: cycle[0],
      text: `dependency cycle: ${cycle.join(" → ")}`,
    });
  }

  if (
    data.provenance.equation_fidelity
    && data.provenance.equation_fidelity !== "exact"
  ) {
    out.push({
      severity: "LOW",
      rule: "degraded-math",
      nodeId: data.nodes[0]?.id ?? "",
      text: `equations extracted via ${data.provenance.equation_fidelity} — distrust exact forms`,
    });
  }

  for (const [id, note] of Object.entries(data.notes)) {
    if (note.unresolved?.length) {
      out.push({
        severity: "LOW",
        rule: "unresolved-note",
        nodeId: id,
        text: `open questions: ${note.unresolved.join("; ")}`,
      });
    }
  }

  const vals = Object.values(data.centrality).sort((a, b) => a - b);
  const p90 = vals[Math.floor(vals.length * 0.9)] ?? Infinity;
  for (const [id, centrality] of Object.entries(data.centrality)) {
    if (vals.length > 1 && centrality >= p90 && centrality > 0) {
      out.push({
        severity: "MED",
        rule: "bottleneck",
        nodeId: id,
        text: `bridge node (betweenness ${centrality}) — many paths run through it`,
      });
    }
  }

  const order = { HIGH: 0, MED: 1, LOW: 2 };
  return out.sort((a, b) => order[a.severity] - order[b.severity]);
}
