import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import LookupChip from "./LookupChip";

/* Suppressing the misses was not enough: selecting a concept label still put a
   dialog on screen unasked. The offer is now a chip the reader can ignore, and
   the explanation only opens when they ask for it. */
describe("LookupChip", () => {
  it("offers the lookup without giving it", () => {
    const html = renderToStaticMarkup(
      <LookupChip onOpen={() => {}} phrase="Adjustment Set" />,
    );

    expect(html).toContain("Look up");
    // The definition itself must not be here — that is the whole point.
    expect(html).not.toContain("role=\"dialog\"");
  });

  it("names what will be looked up, so the reader knows before clicking", () => {
    const html = renderToStaticMarkup(
      <LookupChip onOpen={() => {}} phrase="Adjustment Set" />,
    );

    expect(html).toContain("Adjustment Set");
  });

  it("is a button, not a link that goes nowhere", () => {
    const html = renderToStaticMarkup(
      <LookupChip onOpen={() => {}} phrase="Adjustment Set" />,
    );

    expect(html).toContain("<button");
    expect(html).toContain('type="button"');
  });

  it("shortens a long phrase rather than stretching across the page", () => {
    const html = renderToStaticMarkup(
      <LookupChip
        onOpen={() => {}}
        phrase="a rather long selected phrase that would not fit on a chip"
      />,
    );

    expect(html).toContain("…");
    expect(html.length).toBeLessThan(400);
  });
});
