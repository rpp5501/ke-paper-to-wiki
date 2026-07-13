import { renderToStaticMarkup } from "react-dom/server";
import { beforeEach, describe, expect, it } from "vitest";

import App from "./App";
import { KE_DATA } from "./data.gen";
import { useApp } from "./store";

beforeEach(() => {
  useApp.setState({
    layoutPhase: "loading",
    navigationRequestId: 0,
    pendingNavigation: null,
  } as never);
});

describe("App", () => {
  it("renders the local graph workbench in its layout-loading state", () => {
    const markup = renderToStaticMarkup(<App />);

    expect(markup).toContain('class="shell"');
    expect(markup).toContain('id="left-panel"');
    expect(markup).toContain('id="topbar"');
    expect(markup).toContain('id="drawer"');
    expect(markup).toContain(`Laying out ${KE_DATA.nodes.length} nodes…`);
    expect(markup).not.toContain("nodes loaded");
  });

  it("renders diagnostic and view semantics with a disabled search reason", () => {
    const markup = renderToStaticMarkup(<App />);

    expect(markup).toContain('role="complementary"');
    expect(markup).toContain('role="tablist"');
    expect(markup).toContain('role="radiogroup"');
    expect(markup).toContain('placeholder="search… (Enter)"');
    expect(markup).toContain('aria-describedby="search-disabled-reason"');
    expect(markup).toContain('title="Graph layout is still loading."');
    expect(markup).toContain('id="search-disabled-reason"');
  });
});
