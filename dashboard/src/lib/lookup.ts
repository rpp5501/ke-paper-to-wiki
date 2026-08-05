// Select-to-look-up: resolve a highlighted phrase against what the bundle
// already knows, in order of how specific the answer is. The hover glossary
// only fires on terms someone wrote a note for; this covers the ones it missed.
//
// Pure, so it tests under vitest's `environment: "node"`. The DOM half lives in
// components/SelectionLookup.tsx.
import type { SourceSection } from "./source";

export type LookupData = {
  glossary: Record<string, string>;
  nodes: { id: string; label: string; tldr?: string }[];
  sections: Record<string, SourceSection>;
};

export type LookupResult =
  | { kind: "glossary"; term: string; definition: string }
  | { kind: "concept"; nodeId: string; label: string; definition: string }
  | { kind: "section"; ref: string; title: string; excerpt: string };

/** A selection longer than this is a sentence someone highlighted to read,
 *  not a term they want explained. */
const MAX_WORDS = 8;
const EXCERPT_CHARS = 240;

const normalise = (value: string) =>
  value.trim().toLowerCase().replace(/\s+/g, " ").replace(/e?s$/, "");

function excerptAround(text: string, at: number): string {
  const start = Math.max(0, at - EXCERPT_CHARS / 2);
  const end = Math.min(text.length, at + EXCERPT_CHARS / 2);
  return (start > 0 ? "…" : "") + text.slice(start, end).trim()
    + (end < text.length ? "…" : "");
}

export function lookup(phrase: string, data: LookupData): LookupResult | null {
  const raw = phrase.trim();
  if (!raw || raw.split(/\s+/).length > MAX_WORDS) return null;
  const key = normalise(raw);

  for (const [term, definition] of Object.entries(data.glossary)) {
    if (normalise(term) === key) return { kind: "glossary", term, definition };
  }

  for (const node of data.nodes) {
    if (normalise(node.label) === key) {
      return {
        kind: "concept", nodeId: node.id, label: node.label,
        definition: node.tldr ?? "",
      };
    }
  }

  const needle = raw.toLowerCase();
  for (const [ref, section] of Object.entries(data.sections)) {
    const at = section.text.toLowerCase().indexOf(needle);
    if (at >= 0) {
      return {
        kind: "section", ref, title: section.title,
        excerpt: excerptAround(section.text, at),
      };
    }
  }

  // No match is an answer. Returning the nearest paragraph would dress a miss
  // up as a hit, which is worse than saying nothing.
  return null;
}

/** True when the selection sits inside a term the hover already explains --
 *  two explanations stacked on one phrase is worse than one. */
export function insideKnownTerm(
  phrase: string,
  glossary: Record<string, string>,
): boolean {
  const key = normalise(phrase);
  if (!key) return false;
  return Object.keys(glossary).some((term) => {
    const full = normalise(term);
    return full !== key && full.includes(key);
  });
}
