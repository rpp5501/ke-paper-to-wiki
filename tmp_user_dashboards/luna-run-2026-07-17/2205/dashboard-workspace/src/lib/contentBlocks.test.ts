import { describe, expect, it } from "vitest";

import { parseContent } from "./contentBlocks";

describe("parseContent", () => {
  it("passes plain markdown through as one segment", () => {
    expect(parseContent("hello $x$")).toEqual([
      { type: "markdown", markdown: "hello $x$" },
    ]);
  });

  it("parses an annotated-eq fence between markdown", () => {
    const src = [
      "before",
      "",
      "```annotated-eq",
      "latex: 'E = mc^2'",
      "terms:",
      "  - tex: 'E'",
      "    role: 1",
      "    words: 'energy'",
      "```",
      "",
      "after",
    ].join("\n");
    const segs = parseContent(src);
    expect(segs).toHaveLength(3);
    expect(segs[0]).toEqual({ type: "markdown", markdown: "before" });
    expect(segs[1]).toMatchObject({
      type: "annotated-eq",
      latex: "E = mc^2",
      terms: [{ tex: "E", role: 1, words: "energy" }],
    });
    expect(segs[2]).toEqual({ type: "markdown", markdown: "after" });
  });

  it("parses derivation, algorithm, figure fences", () => {
    const src = [
      "```derivation",
      "shape: 'maps a group to a score'",
      "steps:",
      "  - latex: 'a = b'",
      "    why: 'definition'",
      "```",
      "",
      "```algorithm",
      "title: 'Rank groups'",
      "lines:",
      "  - code: 'for g in groups:'",
      "    intent: 'visit each group'",
      "```",
      "",
      "```figure",
      "id: comet-plot",
      "caption: 'Confidence comets'",
      "```",
    ].join("\n");
    const segs = parseContent(src);
    expect(segs.map((s) => s.type)).toEqual(["derivation", "algorithm", "figure"]);
    expect(segs[0]).toMatchObject({
      shape: "maps a group to a score",
      steps: [{ latex: "a = b", why: "definition" }],
    });
    expect(segs[1]).toMatchObject({
      title: "Rank groups",
      lines: [{ code: "for g in groups:", intent: "visit each group" }],
    });
    expect(segs[2]).toMatchObject({ id: "comet-plot", caption: "Confidence comets" });
  });

  it("leaves ordinary code fences as markdown", () => {
    const src = "```python\nprint('hi')\n```";
    expect(parseContent(src)).toEqual([{ type: "markdown", markdown: src }]);
  });

  it("throws on malformed payload", () => {
    expect(() => parseContent("```annotated-eq\nterms: []\n```")).toThrow(/content-block/);
    expect(() => parseContent("```derivation\nsteps: []\n```")).toThrow(/content-block/);
    expect(() => parseContent("```figure\ncaption: 'x'\n```")).toThrow(/content-block/);
  });
});
