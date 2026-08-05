import { describe, expect, it } from "vitest";

import { insideKnownTerm, lookup, type LookupData } from "./lookup";

const DATA: LookupData = {
  glossary: { "d-separation": "A graphical criterion.", CPDAG: "An equivalence class." },
  nodes: [
    { id: "sid", label: "Structural Intervention Distance (SID)",
      tldr: "A pre-metric over causal graphs." },
  ],
  sections: {
    "3": { title: "Algorithms", text: "The adjustment criterion has two conditions." },
    "4": { title: "Proofs", text: "Repeated squaring reaches the transitive closure." },
  },
};

describe("lookup cascade", () => {
  it("finds a glossary term first", () => {
    expect(lookup("d-separation", DATA)).toEqual({
      kind: "glossary", term: "d-separation", definition: "A graphical criterion.",
    });
  });

  it("normalises case", () => {
    expect(lookup("cpdag", DATA)?.kind).toBe("glossary");
  });

  it("normalises a plural", () => {
    expect(lookup("CPDAGs", DATA)?.kind).toBe("glossary");
  });

  it("falls through to a concept node, returning its id to navigate to", () => {
    const hit = lookup("Structural Intervention Distance (SID)", DATA);
    expect(hit).toEqual({
      kind: "concept", nodeId: "sid",
      label: "Structural Intervention Distance (SID)",
      definition: "A pre-metric over causal graphs.",
    });
  });

  it("falls through to a paper section, with the ref the SourceChip needs", () => {
    const hit = lookup("adjustment criterion", DATA);
    expect(hit?.kind).toBe("section");
    if (hit?.kind !== "section") throw new Error("expected a section hit");
    expect(hit.ref).toBe("3");
    expect(hit.excerpt).toContain("adjustment criterion");
  });

  it("returns null rather than a loosely related paragraph", () => {
    expect(lookup("quantum chromodynamics", DATA)).toBeNull();
  });

  it("ignores an empty or whitespace selection", () => {
    expect(lookup("   ", DATA)).toBeNull();
  });

  it("ignores a selection long enough to be a sentence, not a term", () => {
    expect(lookup(
      "the adjustment criterion has two conditions and both of them matter here",
      DATA)).toBeNull();
  });
});

describe("deferring to the existing hover", () => {
  it("reports a selection that lies inside a known glossary term", () => {
    expect(insideKnownTerm("separation", DATA.glossary)).toBe(true);
  });

  it("does not report an unrelated selection", () => {
    expect(insideKnownTerm("criterion", DATA.glossary)).toBe(false);
  });
});
