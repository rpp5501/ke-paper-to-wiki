import { describe, expect, it } from "vitest";

import {
  DEFAULT_PANEL_WIDTHS,
  PANEL_STORAGE_KEY,
  panelBounds,
  readPanelWidths,
  resolveExplorePanelWidths,
  widthFromKeyboard,
  writePanelWidths,
} from "./panelSizing";

describe("panel sizing", () => {
  it("uses the approved defaults and ranges", () => {
    expect(DEFAULT_PANEL_WIDTHS).toEqual({
      "guided-rail": 264,
      diagnostics: 300,
      explanation: 380,
    });
    expect(panelBounds("guided-rail", 700)).toEqual({ min: 220, max: 328 });
  });

  it("keeps a 360px workspace when both Explore panels are inline", () => {
    const widths = resolveExplorePanelWidths(
      { "guided-rail": 264, diagnostics: 480, explanation: 640 },
      1280,
      true,
    );

    expect(widths.diagnostics + widths.explanation).toBeLessThanOrEqual(896);
    expect(widths.diagnostics).toBeGreaterThanOrEqual(240);
    expect(widths.explanation).toBeGreaterThanOrEqual(320);
  });

  it("does not reserve drawer width while the drawer is closed", () => {
    expect(resolveExplorePanelWidths(DEFAULT_PANEL_WIDTHS, 1280, false)).toMatchObject({
      diagnostics: 300,
      explanation: 380,
    });
  });

  it("handles arrows, shifted arrows, Home, End, and unrelated keys", () => {
    const bounds = { min: 240, max: 480 };
    expect(widthFromKeyboard("ArrowRight", false, 300, bounds)).toBe(316);
    expect(widthFromKeyboard("ArrowLeft", true, 300, bounds)).toBe(252);
    expect(widthFromKeyboard("Home", false, 300, bounds)).toBe(240);
    expect(widthFromKeyboard("End", false, 300, bounds)).toBe(480);
    expect(widthFromKeyboard("Escape", false, 300, bounds)).toBeNull();
  });

  it("round-trips versioned widths and recovers from corrupt storage", () => {
    const memory = new Map<string, string>();
    const storage = {
      getItem: (key: string) => memory.get(key) ?? null,
      setItem: (key: string, value: string) => {
        memory.set(key, value);
      },
    };

    writePanelWidths(storage, { ...DEFAULT_PANEL_WIDTHS, diagnostics: 412 });
    expect(readPanelWidths(storage).diagnostics).toBe(412);

    memory.set(PANEL_STORAGE_KEY, "not json");
    expect(readPanelWidths(storage)).toEqual(DEFAULT_PANEL_WIDTHS);
  });

  it("falls back safely when browser storage is blocked", () => {
    const blocked = {
      getItem: () => {
        throw new Error("blocked");
      },
      setItem: () => {
        throw new Error("blocked");
      },
    };

    expect(readPanelWidths(blocked)).toEqual(DEFAULT_PANEL_WIDTHS);
    expect(() => writePanelWidths(blocked, DEFAULT_PANEL_WIDTHS)).not.toThrow();
  });
});
