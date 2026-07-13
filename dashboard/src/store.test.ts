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
    sidebarTab: "insights",
  });
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
    });

    useApp.getState().step(-1);
    expect(useApp.getState().player?.idx).toBe(0);

    useApp.getState().step(1);
    useApp.getState().step(1);
    expect(useApp.getState().player?.idx).toBe(1);
  });
});
