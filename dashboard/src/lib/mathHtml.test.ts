import { describe, expect, it } from "vitest";

import {
  preserveMathForMarkdown,
  renderMathToString,
  restoreMathEscapedDollars,
  safeKatexOptions,
  safeKatexPluginOptions,
  splitTiers,
  tokenizeRichText,
} from "./mathHtml";

const ATTACK_SET = String.raw`$$
\mathbb{D}_{\text{attack}} \;=\; \big\{\, \big((n(x), y),\; s_i\big) \;:\; |Y_{\text{match}}(x)| = 1,\; i \in Y_{\text{match}}(x) \,\big\}
$$`;

describe("preserveMathForMarkdown", () => {
  it("normalizes complete legacy inline math for remark-math", () => {
    expect(
      preserveMathForMarkdown(String.raw`Scale by \(\sqrt{d_k}\).`),
    ).toBe(String.raw`Scale by $\sqrt{d_k}$.`);
  });

  it("leaves display math, code, and incomplete legacy spans unchanged", () => {
    const markdown = "$$\\sqrt{d_k}$$\n\n"
      + "\\(unfinished\n\n"
      + "`\\(inline_code\\)`\n\n"
      + "```tex\n"
      + "\\(fenced_code\\)\n"
      + "```";

    expect(preserveMathForMarkdown(markdown)).toBe(markdown);
  });

  it("continues normalizing after an incomplete legacy span", () => {
    const markdown = "\\(unfinished\n\nThen \\(x\\).";

    expect(preserveMathForMarkdown(markdown)).toBe(
      "\\(unfinished\n\nThen $x$.",
    );
  });

  it("protects trailing escaped-dollar TeX without merging delimiters", () => {
    const markdown = String.raw`$2\$$`;
    const preserved = preserveMathForMarkdown(markdown);

    expect(preserved).not.toMatch(/^\$\$/);
    expect(restoreMathEscapedDollars(preserved)).toBe(markdown);
  });

  it("treats a dollar after an even backslash run as a closing delimiter", () => {
    const markdown = String.raw`$x\\$ price \$5 and $z$`;
    const preserved = preserveMathForMarkdown(markdown);

    expect(preserved).toBe(String.raw`$x\\$ price ` + "\uE000" + String.raw`5 and $z$`);
  });

  it("treats a dollar after an even backslash run as a math opener", () => {
    const markdown = String.raw`\\$x$`;

    expect(preserveMathForMarkdown(markdown)).toBe(markdown);
  });

  it("keeps a dollar after an odd backslash run as escaped prose", () => {
    const markdown = String.raw`\$x$`;

    expect(preserveMathForMarkdown(markdown)).toBe("\uE000x$");
  });
});

describe("splitTiers", () => {
  it("extracts all five headed explanation tiers", () => {
    const tiers = splitTiers(`
# Scaled dot-product attention

## TL;DR {#tldr}
short answer

## Intuition {#intuition}
mental model

## Mechanics {#mechanics}
step by step

## The Math {#the-math}
$$\\sqrt{d_k}$$

## Go Deeper {#go-deeper}
further reading
`);

    expect(Object.keys(tiers)).toEqual([
      "tldr",
      "intuition",
      "mechanics",
      "the-math",
      "go-deeper",
    ]);
    expect(tiers.tldr).toBe("short answer");
    expect(tiers["the-math"]).toBe(String.raw`$$\sqrt{d_k}$$`);
  });
});

describe("tokenizeRichText", () => {
  it("emits display and inline math tokens without losing delimiters", () => {
    const tokens = tokenizeRichText(
      String.raw`Scale by $$\sqrt{d_k}$$, then apply \(\operatorname{softmax}(x)\).`,
      {},
    );

    expect(tokens.filter((token) => token.kind === "math")).toEqual([
      {
        kind: "math",
        source: String.raw`$$\sqrt{d_k}$$`,
        tex: String.raw`\sqrt{d_k}`,
        display: true,
      },
      {
        kind: "math",
        source: String.raw`\(\operatorname{softmax}(x)\)`,
        tex: String.raw`\operatorname{softmax}(x)`,
        display: false,
      },
    ]);
  });

  it("matches the longest glossary term at real word boundaries", () => {
    const tokens = tokenizeRichText(
      "softmax soft software resoftmax",
      {
        soft: "a normalized score",
        softmax: "a normalized exponential distribution",
      },
    );

    expect(
      tokens
        .filter((token) => token.kind === "glossary")
        .map((token) => token.value),
    ).toEqual(["softmax", "soft"]);
  });

  it("does not match a glossary term across a hyphenated word boundary", () => {
    const tokens = tokenizeRichText("soft soft-max", {
      soft: "a normalized score",
    });

    expect(tokens.filter((token) => token.kind === "glossary")).toHaveLength(1);
  });

  it("keeps glossary definitions as inert token data", () => {
    const definition = '\"><img src=x onerror="alert(1)">';
    const token = tokenizeRichText("Q", { Q: definition }).find(
      (candidate) => candidate.kind === "glossary",
    );

    expect(token).toMatchObject({ kind: "glossary", value: "Q", definition });
    expect(token).not.toHaveProperty("html");
  });
});

describe("renderMathToString", () => {
  it("renders the reported attack-set equation with KaTeX", () => {
    const html = renderMathToString(ATTACK_SET);

    expect(html).toContain("katex-display");
    expect(html).not.toContain(ATTACK_SET);
  });

  it("shares one locked-down KaTeX option source with DOM rendering", () => {
    expect(safeKatexOptions(true)).toMatchObject({
      displayMode: true,
      output: "html",
      strict: "error",
      throwOnError: true,
      trust: false,
    });
    expect(safeKatexPluginOptions()).toMatchObject({
      output: "html",
      strict: "error",
      throwOnError: false,
      trust: false,
    });
  });

  it("renders square-root notation with local KaTeX", () => {
    const html = renderMathToString(String.raw`$$\sqrt{d_k}$$`);

    expect(html).toContain("katex");
    expect(html).toContain("sqrt");
    expect(html).not.toContain(String.raw`$$\sqrt{d_k}$$`);
  });

  it("returns the original delimited source when KaTeX rejects the TeX", () => {
    const invalid = String.raw`\(\definitelyNotARealKatexCommand{\)`;

    expect(renderMathToString(invalid)).toBe(invalid);
  });
});

// remark-math treats whatever sits on the same line as an opening block `$$`
// as an INFO STRING -- the same way ```python tags a code fence -- and drops
// it. Pages write the equation on that line, so `$$\begin{aligned}` lost its
// environment and KaTeX got a body starting with a bare `&`, reporting
// "Expected 'EOF', got '&'". 7 of 24 shipped pages showed raw LaTeX or a red
// katex-error because of it, and normalize_math's `aligned` wrapper made it
// more likely by putting an environment right after the delimiter.
describe("block math must not put content on the opening delimiter line", () => {
  const D = "$".repeat(2);

  it("moves same-line content onto its own line", () => {
    const out = preserveMathForMarkdown(`${D}\begin{aligned}\na &= b\n\end{aligned}${D}`);
    expect(out.startsWith(`${D}\n\begin{aligned}`)).toBe(true);
  });

  it("leaves a block that is already well-formed alone", () => {
    const good = `${D}\n\begin{aligned}\na &= b\n\end{aligned}\n${D}`;
    expect(preserveMathForMarkdown(good)).toBe(good);
  });

  it("closes on its own line too", () => {
    const out = preserveMathForMarkdown(`${D}\na = b${D}`);
    expect(out.endsWith(`\n${D}`)).toBe(true);
  });

  it("leaves inline math inside a sentence alone", () => {
    const text = `The value $x$ is fine.`;
    expect(preserveMathForMarkdown(text)).toBe(text);
  });

  it("leaves a fenced code block alone", () => {
    const fenced = "```algorithm\nlines:\n  - code: \"a\"\n```";
    expect(preserveMathForMarkdown(fenced)).toBe(fenced);
  });
});

describe("the anchor that follows a closing $$", () => {
  const D = "$".repeat(2);

  it("moves to its own line so the block can close", () => {
    const out = preserveMathForMarkdown(`${D}\n\begin{aligned}\na &= b\n\end{aligned}${D} [eq_9]`);
    expect(out).toBe(`${D}\n\begin{aligned}\na &= b\n\end{aligned}\n${D}\n[eq_9]`);
  });

  it("keeps prose after the block on its own line too", () => {
    const out = preserveMathForMarkdown(`${D}\nx = 1\n${D} [eq_1]\n\nNext paragraph.`);
    expect(out).toContain(`${D}\n[eq_1]`);
    expect(out).toContain("Next paragraph.");
  });
});
