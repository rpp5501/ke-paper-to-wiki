import { parse as parseYaml } from "yaml";

export type AnnotatedEqTerm = { tex: string; role: 1 | 2 | 3 | 4 | 5; words: string };
export type AnnotatedEqBlock = {
  type: "annotated-eq";
  latex: string;
  terms: AnnotatedEqTerm[];
};
export type DerivationBlock = {
  type: "derivation";
  shape?: string;
  steps: { latex: string; why: string }[];
};
export type AlgorithmBlock = {
  type: "algorithm";
  title?: string;
  lines: { code: string; intent: string }[];
};
export type FigureBlock = {
  type: "figure";
  id: string;
  caption?: string;
  props?: Record<string, unknown>;
};
export type MermaidBlock = { type: "mermaid"; code: string };
export type MarkdownSegment = { type: "markdown"; markdown: string };
export type ContentSegment =
  | MarkdownSegment
  | AnnotatedEqBlock
  | DerivationBlock
  | AlgorithmBlock
  | FigureBlock
  | MermaidBlock;

const BLOCK_TYPES = new Set([
  "annotated-eq", "derivation", "algorithm", "figure", "mermaid",
]);
const FENCE = /^```([\w-]+)\r?\n([\s\S]*?)\r?\n```$/;

export function parseContent(markdown: string): ContentSegment[] {
  const out: ContentSegment[] = [];
  const pieces = markdown.split(/(^```[\w-]+\r?\n[\s\S]*?\r?\n```$)/m);
  for (const piece of pieces) {
    const match = piece.match(FENCE);
    if (!match || !BLOCK_TYPES.has(match[1])) {
      if (piece.trim()) pushMarkdown(out, piece);
      continue;
    }
    out.push(toBlock(match[1], match[2]));
  }
  return out.length ? out : [{ type: "markdown", markdown }];
}

function pushMarkdown(out: ContentSegment[], piece: string) {
  const last = out[out.length - 1];
  if (last?.type === "markdown") {
    last.markdown = `${last.markdown}\n\n${piece.trim()}`;
  } else {
    out.push({ type: "markdown", markdown: piece.trim() });
  }
}

function fail(kind: string, message: string): never {
  throw new Error(`content-block: ${kind}: ${message}`);
}

function asString(kind: string, data: Record<string, unknown>, key: string): string {
  const value = data[key];
  if (typeof value !== "string" || value.length === 0) {
    fail(kind, `missing or non-string '${key}'`);
  }
  return value;
}

function optionalString(
  kind: string,
  data: Record<string, unknown>,
  key: string,
): string | undefined {
  if (data[key] === undefined || data[key] === null) return undefined;
  return asString(kind, data, key);
}

function asItems(kind: string, data: Record<string, unknown>, key: string): unknown[] {
  const value = data[key];
  if (!Array.isArray(value) || value.length === 0) {
    fail(kind, `missing or empty '${key}' list`);
  }
  return value;
}

function asRecord(kind: string, item: unknown, where: string): Record<string, unknown> {
  if (typeof item !== "object" || item === null || Array.isArray(item)) {
    fail(kind, `each ${where} entry must be a mapping`);
  }
  return item as Record<string, unknown>;
}

function toBlock(kind: string, body: string): ContentSegment {
  // Mermaid is diagram source, not a YAML payload; it never reaches the parser.
  if (kind === "mermaid") return { type: "mermaid", code: body };

  let data: Record<string, unknown>;
  try {
    const parsed = parseYaml(body);
    data = asRecord(kind, parsed, "payload");
  } catch (error) {
    if (error instanceof Error && error.message.startsWith("content-block:")) throw error;
    fail(kind, `invalid YAML (${String(error)})`);
  }

  if (kind === "annotated-eq") {
    const terms = asItems(kind, data, "terms").map((item) => {
      const term = asRecord(kind, item, "terms");
      const role = term.role;
      if (typeof role !== "number" || role < 1 || role > 5 || !Number.isInteger(role)) {
        fail(kind, "each term needs an integer 'role' between 1 and 5");
      }
      return {
        tex: asString(kind, term, "tex"),
        role: role as AnnotatedEqTerm["role"],
        words: asString(kind, term, "words"),
      };
    });
    return { type: "annotated-eq", latex: asString(kind, data, "latex"), terms };
  }

  if (kind === "derivation") {
    const steps = asItems(kind, data, "steps").map((item) => {
      const step = asRecord(kind, item, "steps");
      return { latex: asString(kind, step, "latex"), why: asString(kind, step, "why") };
    });
    return { type: "derivation", shape: optionalString(kind, data, "shape"), steps };
  }

  if (kind === "algorithm") {
    const lines = asItems(kind, data, "lines").map((item) => {
      const line = asRecord(kind, item, "lines");
      return { code: asString(kind, line, "code"), intent: asString(kind, line, "intent") };
    });
    return { type: "algorithm", title: optionalString(kind, data, "title"), lines };
  }

  const props = data.props === undefined
    ? undefined
    : asRecord(kind, data.props, "props");
  return {
    type: "figure",
    id: asString(kind, data, "id"),
    caption: optionalString(kind, data, "caption"),
    props,
  };
}
