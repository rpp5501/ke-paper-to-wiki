import { renderToStaticMarkup } from "react-dom/server";
import { beforeEach, describe, expect, it } from "vitest";

import App, {
  autoStartStep,
  drawerAnnouncementFor,
  getEscapeLayer,
  getDrawerLifecycleAction,
  nextDrawerAnnouncement,
  tourIsVisible,
} from "./App";
import { LEARN_STEPS } from "./components/LearnPanel";
import Sidebar from "./components/Sidebar";
import { KE_DATA } from "./data.gen";
import { useApp } from "./store";

beforeEach(() => {
  useApp.setState({
    selected: null,
    hoverEq: null,
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
    expect(markup).not.toContain('id="drawer"');
    expect(markup).toContain(`Laying out ${KE_DATA.nodes.length} nodes…`);
    expect(markup).not.toContain("nodes loaded");
  });

  it("renders diagnostic and view semantics with a disabled search reason", () => {
    const markup = renderToStaticMarkup(<App />);

    expect(markup).toContain('role="complementary"');
    expect(markup).toContain('role="radiogroup"');
    expect(markup).toContain('placeholder="Find a concept… (Enter)"');
    expect(markup).toContain('aria-describedby="search-disabled-reason"');
    expect(markup).toContain('title="Graph layout is still loading."');
    expect(markup).toContain('id="search-disabled-reason"');
  });

  it("lands in learn mode: learning path rendered, diagnostics and tour card absent", () => {
    const markup = renderToStaticMarkup(<App />);
    expect(markup).toContain("ideas that matter");
    expect(markup).toContain("Guided");
    expect(markup).not.toContain("Insights &amp; Health");
    expect(markup).not.toContain("Guided tour");
  });

  it("exposes the diagnostics tablist when rendered directly (explore mode's left rail)", () => {
    // App defaults to learn mode, whose left rail is LearnPanel rather than
    // Sidebar (see the "lands in learn mode" test above). renderToStaticMarkup
    // only ever sees the store's initial state (zustand v5 serves
    // getInitialState() for SSR), so explore mode can't be exercised through
    // <App /> here — render Sidebar directly to preserve the tablist
    // assertion's original intent.
    const markup = renderToStaticMarkup(<Sidebar onCloseSheet={() => {}} />);
    expect(markup).toContain('role="tablist"');
  });

  it("keeps one polite drawer status region mounted while the drawer is closed", () => {
    const markup = renderToStaticMarkup(<App />);

    expect(markup).toContain('id="drawer-live-status"');
    expect(markup).toContain('aria-live="polite"');
    expect(markup).toContain('role="status"');
    expect(markup).not.toContain("Explanation opened.");
    expect(markup).not.toContain("Selected item is unavailable.");
  });

  it("announces invalid and valid selections from the app-owned status model", () => {
    expect(drawerAnnouncementFor("missing-node"))
      .toBe("Selected item is unavailable.");
    expect(drawerAnnouncementFor("scaled-dot-product-attention"))
      .toBe("Scaled Dot-Product Attention selected. Explanation opened.");
  });

  it("clears on close and gives a repeated selection a fresh announcement", () => {
    const initial = { message: "", revision: 0 };
    const firstOpen = nextDrawerAnnouncement(
      initial,
      "scaled-dot-product-attention",
    );
    const closed = nextDrawerAnnouncement(firstOpen, null);
    const secondOpen = nextDrawerAnnouncement(
      closed,
      "scaled-dot-product-attention",
    );

    expect(firstOpen.message).toBe(
      "Scaled Dot-Product Attention selected. Explanation opened.",
    );
    expect(closed.message).toBe("");
    expect(secondOpen.message).toBe(firstOpen.message);
    expect(secondOpen.revision).toBeGreaterThan(firstOpen.revision);
  });

  it("exposes an invalid announcement before the closed state clears it", () => {
    const invalid = nextDrawerAnnouncement(
      { message: "", revision: 0 },
      "missing-node",
    );
    const closed = nextDrawerAnnouncement(invalid, null);

    expect(invalid.message).toBe("Selected item is unavailable.");
    expect(invalid.revision).toBe(1);
    expect(closed.message).toBe("");
  });

  it("plans origin capture, restoration, and modal-only focus deliberately", () => {
    expect(getDrawerLifecycleAction({
      wasOpen: false,
      isOpen: true,
      wasModalOpen: false,
      isModalOpen: false,
      previousSelected: null,
      selected: "attention",
    })).toEqual({ origin: "capture", focus: null });
    expect(getDrawerLifecycleAction({
      wasOpen: false,
      isOpen: true,
      wasModalOpen: false,
      isModalOpen: true,
      previousSelected: null,
      selected: "attention",
    })).toEqual({ origin: "capture", focus: "close" });
    expect(getDrawerLifecycleAction({
      wasOpen: true,
      isOpen: true,
      wasModalOpen: true,
      isModalOpen: true,
      previousSelected: "attention",
      selected: "scaled-dot-product-attention",
    })).toEqual({ origin: null, focus: "heading" });
    expect(getDrawerLifecycleAction({
      wasOpen: true,
      isOpen: false,
      wasModalOpen: false,
      isModalOpen: false,
      previousSelected: "attention",
      selected: null,
    })).toEqual({ origin: "restore", focus: null });
  });

  it("gives visible modal sheets Escape priority over the tour", () => {
    expect(getEscapeLayer({
      drawerModalOpen: true,
      drawerOpen: true,
      sidebarModalOpen: false,
      tourVisible: true,
    })).toBe("drawer");
    expect(getEscapeLayer({
      drawerModalOpen: false,
      drawerOpen: false,
      sidebarModalOpen: true,
      tourVisible: true,
    })).toBe("sidebar");
    expect(getEscapeLayer({
      drawerModalOpen: false,
      drawerOpen: true,
      sidebarModalOpen: false,
      tourVisible: true,
    })).toBe("tour");
    expect(getEscapeLayer({
      drawerModalOpen: false,
      drawerOpen: true,
      sidebarModalOpen: false,
      tourVisible: false,
    })).toBe("drawer");
  });

  it("does not give Escape to a raw tour with no valid node targets", () => {
    const visible = tourIsVisible({
      dismissed: false,
      mode: "explore",
      nodeIds: new Set(["attention"]),
      tour: [{ nodeIds: ["missing-node"] }],
    });

    expect(visible).toBe(false);
    expect(getEscapeLayer({
      drawerModalOpen: false,
      drawerOpen: true,
      sidebarModalOpen: false,
      tourVisible: visible,
    })).toBe("drawer");
  });

  it("hides the tour in learn mode even with valid, non-dismissed steps", () => {
    expect(tourIsVisible({
      dismissed: false,
      mode: "learn",
      nodeIds: new Set(["attention"]),
      tour: [{ nodeIds: ["attention"] }],
    })).toBe(false);
  });

  describe("autoStartStep", () => {
    const base = {
      mode: "learn" as const,
      layoutPhase: "ready" as const,
      tourIdx: null,
      selected: null,
      steps: LEARN_STEPS,
    };

    it("starts step 1 exactly once when learn mode is ready and idle", () => {
      expect(autoStartStep(base)).toEqual({
        index: 0,
        nodeId: LEARN_STEPS[0].nodeId,
      });
    });

    it("does not fire in explore mode, before layout, mid-tour, with a selection, or with no steps", () => {
      expect(autoStartStep({ ...base, mode: "explore" })).toBeNull();
      expect(autoStartStep({ ...base, layoutPhase: "loading" })).toBeNull();
      expect(autoStartStep({ ...base, tourIdx: 0 })).toBeNull();
      expect(autoStartStep({ ...base, selected: "transformer" })).toBeNull();
      expect(autoStartStep({ ...base, steps: [] })).toBeNull();
    });
  });

});
