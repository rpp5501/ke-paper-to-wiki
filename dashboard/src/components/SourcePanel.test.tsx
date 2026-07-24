import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { SourcePanelPresentation } from "./SourcePanel";

const entry = { ref: "3.2", title: "SDPA", text: "the passage text" };

describe("SourcePanelPresentation", () => {
  it("shows the section heading and the passage", () => {
    const html = renderToStaticMarkup(<SourcePanelPresentation entry={entry} />);
    expect(html).toContain("Source: §3.2 SDPA");
    expect(html).toContain("the passage text");
  });

  it("stays closed until the learner asks for the source", () => {
    const html = renderToStaticMarkup(<SourcePanelPresentation entry={entry} />);
    expect(html).toContain('class="source-tier"');
    expect(html).not.toContain("open");
  });
});
