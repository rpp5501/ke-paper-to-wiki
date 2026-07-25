import { describe, expect, it } from "vitest";

import { sectionFor, sectionKey, type SourceSection } from "./source";

const sections: Record<string, SourceSection> = {
  "3.2": { title: "SDPA", text: "t" },
};

describe("sectionKey", () => {
  // Shared vectors with the pytest suite for build_data.section_key.
  it.each([
    ["sec_3_2", "3.2"],
    ["sec:3.2", "3.2"],
    ["§3.2", "3.2"],
    ["Sec 3.2.1", "3.2.1"],
    ["", ""],
  ])("normalizes %s to %s", (input, expected) => {
    expect(sectionKey(input)).toBe(expected);
  });

  it("normalizes a missing ref to the empty key", () => {
    expect(sectionKey(null)).toBe("");
    expect(sectionKey(undefined)).toBe("");
  });
});

describe("sectionFor", () => {
  it("resolves a graph ref against a pack-keyed section map", () => {
    expect(sectionFor("sec:3.2", sections)).toEqual({
      ref: "3.2",
      title: "SDPA",
      text: "t",
    });
  });

  it("returns undefined for a missing, unknown, or unbacked ref", () => {
    expect(sectionFor(null, sections)).toBeUndefined();
    expect(sectionFor("sec:9.9", sections)).toBeUndefined();
    expect(sectionFor("sec:3.2", {})).toBeUndefined();
  });
});
