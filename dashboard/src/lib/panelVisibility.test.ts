import { describe, expect, it } from "vitest";

import {
  DEFAULT_PANEL_VISIBILITY,
  readPanelVisibility,
  writePanelVisibility,
} from "./panelVisibility";

function memoryStorage(seed: Record<string, string> = {}) {
  const values = new Map(Object.entries(seed));
  return {
    getItem: (key: string) => values.get(key) ?? null,
    setItem: (key: string, value: string) => values.set(key, value),
  };
}

describe("panel visibility persistence", () => {
  it("keeps Guided and Explore visibility as separate preferences", () => {
    const storage = memoryStorage();
    writePanelVisibility(storage, { guidedRail: false, exploreSidebar: true });

    expect(readPanelVisibility(storage)).toEqual({
      guidedRail: false,
      exploreSidebar: true,
    });
  });

  it("falls back safely when stored data is malformed", () => {
    const storage = memoryStorage({
      "paper-dashboard.panel-visibility.v1": "not json",
    });

    expect(readPanelVisibility(storage)).toEqual(DEFAULT_PANEL_VISIBILITY);
  });
});
