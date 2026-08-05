import { describe, expect, it } from "vitest";

import FIXTURE from "./contentBlocksExample.md?raw";
import { parseContent } from "./contentBlocks";

// PAGE_PROMPT shows the writer this exact file as the block syntax to emit.
// Parsing it here is what stops the prompt and the parser drifting apart: a
// field renamed on one side fails on the other instead of shipping pages whose
// blocks silently fall back to raw markdown.
describe("the block syntax PAGE_PROMPT teaches", () => {
  const segments = parseContent(FIXTURE);

  it("parses as blocks, not as markdown", () => {
    expect(segments.map((s) => s.type)).toEqual([
      "algorithm", "derivation", "annotated-eq",
    ]);
  });

  it("keeps every line's intent, which is what the walkthrough renders", () => {
    const algorithm = segments[0];
    if (algorithm.type !== "algorithm") throw new Error("not an algorithm block");
    expect(algorithm.lines).toHaveLength(3);
    expect(algorithm.lines.every((l) => l.intent.length > 0)).toBe(true);
  });

  it("carries an anchor on every explanation, as the lint requires", () => {
    const anchored = /\[(§sec_[\w]+|eq_\d+|S\d+)\]/;
    for (const segment of segments) {
      if (segment.type === "algorithm") {
        segment.lines.forEach((l) => expect(l.intent).toMatch(anchored));
      } else if (segment.type === "derivation") {
        segment.steps.forEach((s) => expect(s.why).toMatch(anchored));
      } else if (segment.type === "annotated-eq") {
        segment.terms.forEach((t) => expect(t.words).toMatch(anchored));
      }
    }
  });
});
