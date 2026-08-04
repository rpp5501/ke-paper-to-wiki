import katex from "katex";
import "katex/dist/katex.min.css";

import { katexMacros } from "./macros";

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

const ESCAPED_DOLLAR_PLACEHOLDER = "\uE000";
const MATH_ESCAPED_DOLLAR_PLACEHOLDER = "\uE001";

export function safeKatexOptions(displayMode: boolean) {
  // The paper's own \newcommand table. Equations are copied verbatim from the
  // source, so without this KaTeX throws on the first private control sequence
  // and the reader is shown raw LaTeX instead of maths.
  return { ...SAFE_KATEX_OPTIONS, displayMode, macros: { ...katexMacros() } };
}

export function safeKatexPluginOptions() {
  return {
    output: SAFE_KATEX_OPTIONS.output,
    strict: SAFE_KATEX_OPTIONS.strict,
    throwOnError: false,
    trust: SAFE_KATEX_OPTIONS.trust,
    macros: { ...katexMacros() },
  };
}

export function restoreEscapedDollars(text: string) {
  return text.replaceAll(ESCAPED_DOLLAR_PLACEHOLDER, "$");
}

export function restoreMathEscapedDollars(text: string) {
  return text.replaceAll(MATH_ESCAPED_DOLLAR_PLACEHOLDER, String.raw`\$`);
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

function hasOddBackslashRun(text: string, index: number) {
  let count = 0;
  while (text[index - count - 1] === "\\") count += 1;
  return count % 2 === 1;
}

function findClosingInlineMathDollar(text: string, from: number) {
  let close = text.indexOf("$", from);
  while (close >= 0 && hasOddBackslashRun(text, close)) {
    close = text.indexOf("$", close + 1);
  }
  return close;
}

function protectMathEscapedDollars(tex: string) {
  return tex.replace(/\\+\$/g, (match) => {
    const slashCount = match.length - 1;
    return slashCount % 2 === 1
      ? "\\".repeat(slashCount - 1) + MATH_ESCAPED_DOLLAR_PLACEHOLDER
      : match;
  });
}

// Prepare prose for remark-math: normalize legacy spans and escaped dollars.
function normalizeLegacyMathInProse(text: string): string {
  let output = "";
  let cursor = 0;

  while (cursor < text.length) {
    if (text[cursor] === "`") {
      let ticks = 1;
      while (text[cursor + ticks] === "`") ticks += 1;
      const delimiter = "`".repeat(ticks);
      const close = text.indexOf(delimiter, cursor + ticks);
      if (close < 0) return output + text.slice(cursor);
      output += text.slice(cursor, close + ticks);
      cursor = close + ticks;
      continue;
    }

    if (text[cursor] === "$" && hasOddBackslashRun(text, cursor)) {
      output = output.slice(0, -1) + ESCAPED_DOLLAR_PLACEHOLDER;
      cursor += 1;
      continue;
    }

    if (text.startsWith("$$", cursor)) {
      const close = text.indexOf("$$", cursor + 2);
      if (close < 0) return output + text.slice(cursor);
      output += text.slice(cursor, close + 2);
      cursor = close + 2;
      continue;
    }

    if (text[cursor] === "$") {
      const close = findClosingInlineMathDollar(text, cursor + 1);
      if (close >= 0) {
        const tex = text.slice(cursor + 1, close);
        output += `$${protectMathEscapedDollars(tex)}$`;
        cursor = close + 1;
        continue;
      }
    }

    if (text.startsWith(String.raw`\(`, cursor)) {
      const close = text.indexOf(String.raw`\)`, cursor + 2);
      const newline = text.indexOf("\n", cursor + 2);
      if (close < 0 || (newline >= 0 && newline < close)) {
        output += String.raw`\(`;
        cursor += 2;
        continue;
      }
      output += `$${protectMathEscapedDollars(text.slice(cursor + 2, close))}$`;
      cursor = close + 2;
      continue;
    }

    output += text[cursor];
    cursor += 1;
  }

  return output;
}

export function preserveMathForMarkdown(markdown: string): string {
  const lines = markdown.match(/[^\n]*(?:\n|$)/g) ?? [];
  let output = "";
  let prose = "";
  let fence: { character: string; length: number } | null = null;

  for (const line of lines) {
    if (!line) continue;
    const withoutNewline = line.endsWith("\n") ? line.slice(0, -1) : line;
    const marker = withoutNewline.match(/^ {0,3}(`{3,}|~{3,})(.*)$/);

    if (fence) {
      output += line;
      if (
        marker
        && marker[1][0] === fence.character
        && marker[1].length >= fence.length
        && marker[2].trim() === ""
      ) {
        fence = null;
      }
      continue;
    }

    if (marker) {
      output += normalizeLegacyMathInProse(prose);
      prose = "";
      output += line;
      fence = { character: marker[1][0], length: marker[1].length };
      continue;
    }

    prose += line;
  }

  return output + normalizeLegacyMathInProse(prose);
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
