import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import MathReveal from "./MathReveal";

describe("MathReveal", () => {
  it("starts closed with the shape and a show-the-math hint", () => {
    const html = renderToStaticMarkup(
      <MathReveal expandAll={false} shape="maps a group to a score">
        <p>full derivation</p>
      </MathReveal>,
    );
    expect(html).not.toContain("<details open");
    expect(html).toContain("maps a group to a score");
    expect(html).toContain("Show the math");
    expect(html).toContain("full derivation"); // stays in DOM for find-in-page
  });

  it("renders open with no hint when expandAll", () => {
    const html = renderToStaticMarkup(
      <MathReveal expandAll shape="maps a group to a score">
        <p>full derivation</p>
      </MathReveal>,
    );
    expect(html).toMatch(/<details[^>]* open/);
    expect(html).not.toContain("Show the math");
  });
});
