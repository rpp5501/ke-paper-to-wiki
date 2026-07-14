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
    tourDismissed: false,
    sidebarTab: "insights",
    layoutPhase: "loading",
    navigationRequestId: 0,
    pendingNavigation: null,
  } as never);
});

describe("useApp", () => {
  it("updates selection and view through the shared actions", () => {
    useApp.getState().setSelected("attention");
    useApp.getState().setView("bridged");

    expect(useApp.getState().selected).toBe("attention");
    expect(useApp.getState().view).toBe("bridged");
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
