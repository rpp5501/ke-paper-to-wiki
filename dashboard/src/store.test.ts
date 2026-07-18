import { beforeEach, describe, expect, it } from "vitest";

import { useApp } from "./store";

beforeEach(() => {
  useApp.setState({
    selected: null,
    view: "concepts",
    hiddenKinds: new Set(),
    blastOn: false,
    hoverEq: null,
    player: null,
    tourIdx: null,
    learnIdx: null,
    tourDismissed: false,
    sidebarTab: "insights",
    layoutPhase: "loading",
    navigationRequestId: 0,
    pendingNavigation: null,
    mode: "learn",
    drawerOpen: false,
    vizFocus: null,
    completedSteps: new Set(),
  } as never);
});

describe("useApp", () => {
  it("updates selection and view through the shared actions", () => {
    useApp.getState().setSelected("attention");
    useApp.getState().setView("bridged");

    expect(useApp.getState().selected).toBe("attention");
    expect(useApp.getState().view).toBe("bridged");
  });

  it("hides and restores details without clearing the selected node", () => {
    useApp.getState().setSelected("attention");
    expect(useApp.getState()).toMatchObject({
      selected: "attention",
      drawerOpen: true,
    });

    useApp.getState().setDrawerOpen(false);
    expect(useApp.getState()).toMatchObject({
      selected: "attention",
      drawerOpen: false,
    });

    useApp.getState().setDrawerOpen(true);
    expect(useApp.getState()).toMatchObject({
      selected: "attention",
      drawerOpen: true,
    });

    useApp.getState().setSelected(null);
    expect(useApp.getState()).toMatchObject({
      selected: null,
      drawerOpen: false,
    });
  });

  it("does not open details without a selected node", () => {
    useApp.getState().setDrawerOpen(true);
    expect(useApp.getState().drawerOpen).toBe(false);
  });

  it("toggles edge kinds without mutating the previous set", () => {
    const previous = useApp.getState().hiddenKinds;

    useApp.getState().toggleKind("implements");

    const hidden = useApp.getState().hiddenKinds;
    expect(hidden).not.toBe(previous);
    expect(hidden).toEqual(new Set(["implements"]));

    useApp.getState().toggleKind("implements");
    expect(useApp.getState().hiddenKinds).toEqual(new Set());
  });

  it("clamps player steps to the available range", () => {
    useApp.getState().setPlayer({
      steps: ["attention", "transformer"],
      idx: 0,
      label: "reading path",
      playing: false,
    });

    useApp.getState().step(-1);
    expect(useApp.getState().player?.idx).toBe(0);

    useApp.getState().step(1);
    useApp.getState().step(1);
    expect(useApp.getState().player?.idx).toBe(1);
  });

  it("dismisses the tour for the current app session", () => {
    const state = useApp.getState() as unknown as {
      dismissTour?: () => void;
    };
    expect(typeof state.dismissTour).toBe("function");
    if (!state.dismissTour) return;

    useApp.getState().setTourIdx(2);
    state.dismissTour();

    expect(useApp.getState()).toMatchObject({
      tourDismissed: true,
      tourIdx: null,
    });
  });

  it("leaves learnIdx intact when explore mode dismisses the tour", () => {
    useApp.getState().setLearnIdx(3);
    useApp.getState().setMode("explore");
    useApp.getState().dismissTour();

    expect(useApp.getState().learnIdx).toBe(3);
  });

  it("publishes graph layout phases", () => {
    const state = useApp.getState() as unknown as {
      layoutPhase?: string;
      setLayoutPhase?: (phase: string) => void;
    };
    expect(typeof state.setLayoutPhase).toBe("function");
    if (!state.setLayoutPhase) return;

    state.setLayoutPhase("error");
    expect((useApp.getState() as unknown as { layoutPhase: string }).layoutPhase)
      .toBe("error");
  });

  it("queues only while ready and supersedes requests monotonically", () => {
    const state = useApp.getState() as unknown as {
      setLayoutPhase?: (phase: string) => void;
      queueNavigation?: (nodeId: string, view: string) => void;
      clearNavigation?: (requestId: number) => void;
    };
    expect(typeof state.queueNavigation).toBe("function");
    expect(typeof state.clearNavigation).toBe("function");
    if (!state.queueNavigation || !state.clearNavigation || !state.setLayoutPhase) return;

    state.queueNavigation("attention", "concepts");
    expect((useApp.getState() as unknown as { pendingNavigation: unknown })
      .pendingNavigation).toBeNull();

    state.setLayoutPhase("ready");
    state.queueNavigation("attention", "concepts");
    expect(useApp.getState()).toMatchObject({
      navigationRequestId: 1,
      pendingNavigation: {
        requestId: 1,
        nodeId: "attention",
        requiredView: "concepts",
      },
      view: "concepts",
    });

    state.queueNavigation("attention-code", "code");
    expect(useApp.getState()).toMatchObject({
      navigationRequestId: 2,
      pendingNavigation: {
        requestId: 2,
        nodeId: "attention-code",
        requiredView: "code",
      },
      view: "code",
    });

    state.clearNavigation(1);
    expect((useApp.getState() as unknown as {
      pendingNavigation: { requestId: number };
    }).pendingNavigation.requestId).toBe(2);

    state.clearNavigation(2);
    expect((useApp.getState() as unknown as { pendingNavigation: unknown })
      .pendingNavigation).toBeNull();
  });
});

describe("mode & learn progress", () => {
  it("opens a gallery visual from Guided mode", () => {
    useApp.getState().openVisualization("scaled-dot-product-attention");

    expect(useApp.getState()).toMatchObject({
      mode: "explore",
      selected: "scaled-dot-product-attention",
      drawerOpen: true,
      vizFocus: "scaled-dot-product-attention",
    });
  });

  it("defaults to learn mode with no completed steps", () => {
    expect(useApp.getState().mode).toBe("learn");
    expect(useApp.getState().completedSteps.size).toBe(0);
  });

  it("switches modes without clearing progress", () => {
    useApp.getState().markStepComplete("attention");
    useApp.getState().setMode("explore");
    expect(useApp.getState().mode).toBe("explore");
    expect(useApp.getState().completedSteps.has("attention")).toBe(true);
  });

  it("toggleExpandAllMath flips the flag, starting closed", () => {
    expect(useApp.getState().expandAllMath).toBe(false);
    useApp.getState().toggleExpandAllMath();
    expect(useApp.getState().expandAllMath).toBe(true);
    useApp.getState().toggleExpandAllMath();
    expect(useApp.getState().expandAllMath).toBe(false);
  });

  it("markStepComplete is idempotent and does not mutate the previous set", () => {
    const before = useApp.getState().completedSteps;
    useApp.getState().markStepComplete("transformer");
    useApp.getState().markStepComplete("transformer");
    const after = useApp.getState().completedSteps;
    expect(after).toEqual(new Set(["transformer"]));
    expect(before.size).toBe(0); // immutability, matches hiddenKinds pattern
  });
});
