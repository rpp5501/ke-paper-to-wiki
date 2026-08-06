export type PanelVisibility = {
  guidedRail: boolean;
  exploreSidebar: boolean;
};

type StorageLike = {
  getItem: (key: string) => string | null;
  setItem: (key: string, value: string) => void;
};

export const PANEL_VISIBILITY_STORAGE_KEY = "paper-dashboard.panel-visibility.v1";
export const DEFAULT_PANEL_VISIBILITY: PanelVisibility = {
  guidedRail: true,
  exploreSidebar: true,
};

export function readPanelVisibility(
  storage?: StorageLike | null,
): PanelVisibility {
  if (!storage) return { ...DEFAULT_PANEL_VISIBILITY };
  try {
    const value = JSON.parse(
      storage.getItem(PANEL_VISIBILITY_STORAGE_KEY) ?? "null",
    ) as Partial<PanelVisibility> | null;
    return {
      guidedRail: typeof value?.guidedRail === "boolean"
        ? value.guidedRail
        : DEFAULT_PANEL_VISIBILITY.guidedRail,
      exploreSidebar: typeof value?.exploreSidebar === "boolean"
        ? value.exploreSidebar
        : DEFAULT_PANEL_VISIBILITY.exploreSidebar,
    };
  } catch {
    return { ...DEFAULT_PANEL_VISIBILITY };
  }
}

export function writePanelVisibility(
  storage: StorageLike | null | undefined,
  visibility: PanelVisibility,
): void {
  if (!storage) return;
  try {
    storage.setItem(PANEL_VISIBILITY_STORAGE_KEY, JSON.stringify(visibility));
  } catch {
    // Storage is best-effort and may be disabled by the browser.
  }
}
