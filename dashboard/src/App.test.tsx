import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import App from "./App";
import { KE_DATA } from "./data.gen";

describe("App", () => {
  it("renders the local graph workbench in its layout-loading state", () => {
    const markup = renderToStaticMarkup(<App />);

    expect(markup).toContain('class="shell"');
    expect(markup).toContain('id="left-panel"');
    expect(markup).toContain('id="topbar"');
    expect(markup).toContain('id="drawer"');
    expect(markup).toContain(`Laying out ${KE_DATA.nodes.length} nodesâ€¦`);
    expect(markup).not.toContain("nodes loaded");
  });
});
