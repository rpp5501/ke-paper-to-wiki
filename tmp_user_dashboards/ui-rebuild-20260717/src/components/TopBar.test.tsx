import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import type { Mode } from "../store";
import { TopBarPresentation } from "./TopBar";

function makeProps(mode: Mode) {
  return {
    blastOn: false,
    expandAllMath: false,
    onToggleExpandAllMath: () => undefined,
    hiddenKinds: new Set<string>(),
    layoutPhase: "ready" as const,
    mode,
    noNodes: false,
    drawerAvailable: false,
    drawerOpen: false,
    onToggleDrawer: () => undefined,
    onToggleSidebar: () => undefined,
    onSetBlastOn: () => undefined,
    onSetMode: () => undefined,
    onSetView: () => undefined,
    onToggleKind: () => undefined,
    sidebarOpen: false,
    sidebarTriggerRef: () => undefined,
    view: "concepts" as const,
  };
}

describe("TopBarPresentation", () => {
  it("learn mode shows only the mode switch, expand-all-math toggle, and search", () => {
    const markup = renderToStaticMarkup(<TopBarPresentation {...makeProps("learn")} />);

    expect(markup).toContain('aria-label="Dashboard mode"');
    expect(markup).toContain("Guided");
    expect(markup).toContain("Explore");
    expect(markup).toContain("Expand all math");
    expect(markup).toContain('aria-pressed="false"');
    expect(markup).toContain("Find a concept");
    expect(markup).not.toContain('aria-label="Graph view"');
    expect(markup).not.toContain("impact radius");
    expect(markup).not.toContain("Open left panel");
    expect(markup).not.toContain("Open right panel");
  });

  it("explore mode shows the full toolbar with plain-language copy", () => {
    const markup = renderToStaticMarkup(<TopBarPresentation {...makeProps("explore")} />);

    expect(markup).toContain('aria-label="Graph view"');
    expect(markup).toContain("impact radius");
    expect(markup).toContain(
      'title="Highlight everything that depends on the selected node"',
    );
    expect(markup).toContain('aria-label="Open left panel"');
    expect(markup).toContain('aria-controls="left-panel"');
    expect(markup).toContain('aria-label="Open right panel"');
    expect(markup).toContain('aria-controls="drawer"');
    expect(markup).toMatch(/aria-label="Open right panel"[^>]*disabled/);
    expect(markup).not.toContain("Diagnostics");
    expect(markup).not.toContain("blast radius");
    expect(markup).not.toContain("Insights / Trace");
    expect(markup).not.toContain("Expand all math");
  });

  it("marks the active mode radio checked", () => {
    const markup = renderToStaticMarkup(<TopBarPresentation {...makeProps("learn")} />);
    const group = markup.split('aria-label="Dashboard mode"')[1].split("</div>")[0];

    expect(group).toContain('aria-checked="true"');
  });

  it("describes both open panels as one-click close actions", () => {
    const markup = renderToStaticMarkup(
      <TopBarPresentation
        {...makeProps("explore")}
        drawerAvailable
        drawerOpen
        sidebarOpen
      />,
    );

    expect(markup).toContain('aria-label="Close left panel"');
    expect(markup).toContain('aria-label="Close right panel"');
    expect(markup).toContain('aria-expanded="true"');
  });
});
