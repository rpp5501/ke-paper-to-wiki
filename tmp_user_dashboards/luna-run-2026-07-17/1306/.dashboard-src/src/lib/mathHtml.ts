import katex from "katex";
import "katex/dist/katex.min.css";

export type RichTextToken =
  | { kind: "text"; value: string }
  | { kind: "glossary"; value: string; definition: string }
  | {
      kind: "math";
      source: string;
      tex: string;
      display: boolean;
    };

export type ExplanationTier =
  | "tldr"
  | "intuition"
  | "mechanics"
  | "the-math"
  | "go-deeper";

export type ExplanationTiers = Partial<Record<ExplanationTier, string>>;

const TIER_IDS = new Set<ExplanationTier>([
  "tldr",
  "intuition",
  "mechanics",
  "the-math",
  "go-deeper",
]);

const SAFE_KATEX_OPTIONS = Object.freeze({
  output: "html" as const,
  strict: "error" as const,
  throwOnError: true,
  trust: false,
});

export function safeKatexOptions(displayMode: boolean) {
  return { ...SAFE_KATEX_OPTIONS, displayMode };
}

const isWordCharacter = (character: string | undefined) => (
  character !== undefined && /[\p{L}\p{N}_-]/u.test(character)
);

function hasWordBoundaries(text: string, start: number, value: string) {
  const first = value[0];
  const last = value[value.length - 1];
  const before = text[start - 1];
  const after = text[start + value.length];
  return !(isWordCharacter(first) && isWordCharacter(before))
    && !(isWordCharacter(last) && isWordCharacter(after));
}

export function splitTiers(markdown: string): ExplanationTiers {
  const tiers: ExplanationTiers = {};
  const heading = /^##\s+.+?\s+\{#(tldr|intuition|mechanics|the-math|go-deeper)\}\s*$/gm;
  const matches = Array.from(markdown.matchAll(heading));

  matches.forEach((match, index) => {
    const id = match[1] as ExplanationTier;
    if (!TIER_IDS.has(id)) return;
    const start = (match.index ?? 0) + match[0].length;
    const end = matches[index + 1]?.index ?? markdown.length;
    tiers[id] = markdown.slice(start, end).trim();
  });

  return tiers;
}

function findNextMath(text: string, from: number) {
  const display = text.indexOf("$$", from);
  const inline = text.indexOf(String.raw`\(`, from);
  if (display < 0) return inline < 0 ? null : { index: inline, delimiter: "inline" as const };
  if (inline < 0 || display < inline) return { index: display, delimiter: "display" as const };
  return { index: inline, delimiter: "inline" as const };
}

function tokenizePlainText(
  value: string,
  glossary: Record<string, string>,
): RichTextToken[] {
  if (!value) return [];
  const terms = Object.keys(glossary)
    .filter(Boolean)
    .sort((left, right) => right.length - left.length || left.localeCompare(right));
  if (terms.length === 0) return [{ kind: "text", value }];

  const tokens: RichTextToken[] = [];
  let cursor = 0;
  while (cursor < value.length) {
    let match: { index: number; term: string } | null = null;
    for (let index = cursor; index < value.length && !match; index += 1) {
      for (const term of terms) {
        if (
          value.startsWith(term, index)
          && hasWordBoundaries(value, index, term)
        ) {
          match = { index, term };
          break;
        }
      }
    }

    if (!match) {
      tokens.push({ kind: "text", value: value.slice(cursor) });
      break;
    }
    if (match.index > cursor) {
      tokens.push({ kind: "text", value: value.slice(cursor, match.index) });
    }
    tokens.push({
      kind: "glossary",
      value: match.term,
      definition: glossary[match.term],
    });
    cursor = match.index + match.term.length;
  }
  return tokens;
}

export function tokenizeRichText(
  text: string,
  glossary: Record<string, string>,
): RichTextToken[] {
  const tokens: RichTextToken[] = [];
  let cursor = 0;

  while (cursor < text.length) {
    const next = findNextMath(text, cursor);
    if (!next) {
      tokens.push(...tokenizePlainText(text.slice(cursor), glossary));
      break;
    }
    if (next.index > cursor) {
      tokens.push(...tokenizePlainText(text.slice(cursor, next.index), glossary));
    }

    const display = next.delimiter === "display";
    const open = display ? "$$" : String.raw`\(`;
    const close = display ? "$$" : String.raw`\)`;
    const contentStart = next.index + open.length;
    const closeIndex = text.indexOf(close, contentStart);
    if (closeIndex < 0) {
      tokens.push(...tokenizePlainText(text.slice(next.index), glossary));
      break;
    }
    const source = text.slice(next.index, closeIndex + close.length);
    tokens.push({
      kind: "math",
      source,
      tex: text.slice(contentStart, closeIndex),
      display,
    });
    cursor = closeIndex + close.length;
  }

  return tokens;
}

// CommonMark treats the backslashes in \(…\) as escapes. Character references
// survive parsing and are decoded back to the original delimiters in text nodes.
// Fenced and inline code are intentionally left literal.
export function preserveInlineMathForMarkdown(markdown: string): string {
  let fenced = false;
  return markdown.split("\n").map((line) => {
    if (/^\s*(```|~~~)/.test(line)) {
      fenced = !fenced;
      return line;
    }
    if (fenced) return line;
    return line.split(/(`+[^`]*`+)/g).map((part, index) => {
      if (index % 2 === 1) return part;
      return part.replace(
        /\\\(([\s\S]+?)\\\)/g,
        (_source, tex: string) => `&#92;(${tex}&#92;)`,
      );
    }).join("");
  }).join("\n");
}

function parseMathSource(source: string) {
  if (source.startsWith("$$") && source.endsWith("$$") && source.length >= 4) {
    return { tex: source.slice(2, -2), displayMode: true };
  }
  if (source.startsWith(String.raw`\(`) && source.endsWith(String.raw`\)`)) {
    return { tex: source.slice(2, -2), displayMode: false };
  }
  return { tex: source, displayMode: false };
}

export function renderMathToString(source: string): string {
  const { tex, displayMode } = parseMathSource(source);
  try {
    return katex.renderToString(tex, {
      ...safeKatexOptions(displayMode),
    });
  } catch {
    return source;
  }
}
