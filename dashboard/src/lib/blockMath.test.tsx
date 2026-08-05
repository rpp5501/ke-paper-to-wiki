// Reader report: raw LaTeX visible in the dashboard, e.g.
//   \begin{array}{rcl} \mathrm{SID}: ... \end{array} $$ [eq_10]
//
// The equations were never the problem -- all 18 display blocks in the pages
// render standalone in KaTeX. remark-math was refusing to parse them, for two
// reasons that only show up in the markdown layer:
//
//  1. Whatever shares the line with an opening block `$$` is read as an INFO
//     STRING, the way ```python tags a fence, and DROPPED. Pages write
//     `$$\begin{aligned}`, so the environment vanished and KaTeX received a
//     body starting with a bare `&`: "Expected 'EOF', got '&'".
//  2. The closing `$$` must also stand alone. Pages write
//     `\end{aligned}$$ [eq_9]`, putting both the environment and the anchor on
//     that line, so the block never closed.
//
// Measured across the shipped pages: 7 of 24 showed raw LaTeX or a red
// katex-error; 0 of 24 after. These cases pin the shapes, so a future change
// to the pipeline cannot quietly reintroduce it.
import ReactMarkdown from "react-markdown";
import rehypeKatex from "rehype-katex";
import remarkMath from "remark-math";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { preserveMathForMarkdown, safeKatexPluginOptions } from "./mathHtml";

const D = "$".repeat(2);
const BODY = "\\begin{aligned}\na &= b \\\\\nc &= d\n\\end{aligned}";

function render(raw: string) {
  return renderToStaticMarkup(
    <ReactMarkdown
      rehypePlugins={[[rehypeKatex, safeKatexPluginOptions()]]}
      remarkPlugins={[[remarkMath, { singleDollarTextMath: true }]]}
    >
      {preserveMathForMarkdown(raw)}
    </ReactMarkdown>,
  );
}

const isDisplayed = (html: string) => (
  html.includes("katex-display")
  && !html.includes("katex-error")
  && !/\\begin\{/.test(html)
);

describe("display math survives the markdown pipeline", () => {
  it("renders when the environment sits on the opening delimiter line", () => {
    expect(isDisplayed(render(`${D}${BODY}\n${D}`))).toBe(true);
  });

  it("renders when the anchor follows the closing delimiter", () => {
    expect(isDisplayed(render(`${D}\n${BODY}\n${D} [eq_9]`))).toBe(true);
  });

  it("renders the shape the pages actually contain", () => {
    expect(isDisplayed(render(`Lead-in [eq_9]:\n\n${D}${BODY}${D} [eq_9]\n`))).toBe(true);
  });

  it("keeps the anchor rather than dropping it", () => {
    expect(render(`${D}\n${BODY}\n${D} [eq_9]`)).toContain("eq_9");
  });

  it("leaves single-line math inline, as it already rendered correctly", () => {
    const html = render(`${D}\\sqrt{d_k}${D}`);
    expect(html).toContain("katex");
    expect(html).not.toContain("katex-display");
  });

  it("leaves a fenced content block untouched", () => {
    const fenced = "```algorithm\nlines:\n  - code: \"a\"\n```";
    expect(preserveMathForMarkdown(fenced)).toBe(fenced);
  });
});
