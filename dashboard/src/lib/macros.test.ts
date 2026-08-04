import { describe, expect, it } from "vitest";

import { katexMacros, sanitizeMacros } from "./macros";

// A paper defines its own notation in its preamble, and latex_pack copies
// equations VERBATIM, so the copied LaTeX calls those commands. Without the
// table KaTeX throws on the first unknown command and renderMathToString falls
// back to printing raw source — the reader sees "\doo" instead of "do".
describe("sanitizeMacros", () => {
  it("keeps well-formed control-sequence definitions", () => {
    const raw = { [String.raw`\G`]: String.raw`\mathcal{G}`,
                  [String.raw`\B`]: String.raw`\mathbf{#1}` };
    expect(sanitizeMacros(raw)).toEqual(raw);
  });

  it("drops keys that are not control sequences", () => {
    const raw = { G: String.raw`\mathcal{G}`, "\\": "x", "": "y" };
    expect(sanitizeMacros(raw)).toEqual({});
  });

  it("drops non-string bodies rather than handing KaTeX a surprise", () => {
    const raw = { [String.raw`\a`]: 1, [String.raw`\b`]: null,
                  [String.raw`\c`]: String.raw`\alpha` };
    expect(sanitizeMacros(raw as Record<string, unknown>))
      .toEqual({ [String.raw`\c`]: String.raw`\alpha` });
  });

  it("returns an empty table for a bundle with no macros", () => {
    expect(sanitizeMacros(undefined)).toEqual({});
  });
});

describe("katexMacros", () => {
  it("is a table KaTeX can consume directly", () => {
    const macros = katexMacros();
    expect(typeof macros).toBe("object");
    for (const [name, body] of Object.entries(macros)) {
      expect(name.startsWith("\\")).toBe(true);
      expect(typeof body).toBe("string");
    }
  });
});
