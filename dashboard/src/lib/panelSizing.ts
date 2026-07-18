export type PanelId = "guided-rail" | "diagnostics" | "explanation";
export type PanelWidths = Record<PanelId, number>;
export type PanelSpec = { defaultWidth: number; min: number; max: number };
export type PanelBounds = { min: number; max: number };

type StorageLike = {
  getItem: (key: string) => string | null;
  setItem: (key: string, value: string) => void;
};

export const MIN_WORKSPACE_WIDTH = 360;
export const RESIZER_SPACE = 12;
export const PANEL_STORAGE_KEY = "paper-dashboard.panel-widths.v1";

export const PANEL_SPECS: Record<PanelId, PanelSpec> = {
  "guided-rail": { defaultWidth: 264, min: 220, max: 420 },
  diagnostics: { defaultWidth: 300, min: 240, max: 480 },
  explanation: { defaultWidth: 380, min: 320, max: 640 },
};

export const DEFAULT_PANEL_WIDTHS: PanelWidths = {
  "guided-rail": 264,
  diagnostics: 300,
  explanation: 380,
};

export function panelBounds(
  id: PanelId,
  viewportWidth: number,
  occupiedWidth = 0,
): PanelBounds {
  const spec = PANEL_SPECS[id];
  return {
    min: spec.min,
    max: Math.max(
      spec.min,
      Math.min(
        spec.max,
        viewportWidth - occupiedWidth - MIN_WORKSPACE_WIDTH - RESIZER_SPACE,
      ),
    ),
  };
}

export function clampPanelWidth(
  id: PanelId,
  width: number,
  viewportWidth: number,
  occupiedWidth = 0,
): number {
  const bounds = panelBounds(id, viewportWidth, occupiedWidth);
  return Math.min(bounds.max, Math.max(bounds.min, Math.round(width)));
}

export function resolveExplorePanelWidths(
  preferred: PanelWidths,
  viewportWidth: number,
  drawerOpen: boolean,
): Pick<PanelWidths, "diagnostics" | "explanation"> {
  const diagnostics = clampPanelWidth("diagnostics", preferred.diagnostics, viewportWidth);
  if (!drawerOpen || viewportWidth < 1280) {
    return {
      diagnostics,
      explanation: clampPanelWidth("explanation", preferred.explanation, viewportWidth),
    };
  }

  const explanation = clampPanelWidth(
    "explanation",
    preferred.explanation,
    viewportWidth,
    diagnostics + RESIZER_SPACE,
  );

  return {
    diagnostics: clampPanelWidth(
      "diagnostics",
      diagnostics,
      viewportWidth,
      explanation + RESIZER_SPACE,
    ),
    explanation,
  };
}

export function widthFromKeyboard(
  key: string,
  shiftKey: boolean,
  current: number,
  bounds: PanelBounds,
): number | null {
  const step = shiftKey ? 48 : 16;
  const next = key === "ArrowLeft"
    ? current - step
    : key === "ArrowRight"
      ? current + step
      : key === "Home"
        ? bounds.min
        : key === "End"
          ? bounds.max
          : null;

  return next === null ? null : Math.min(bounds.max, Math.max(bounds.min, next));
}

export function readPanelWidths(storage?: StorageLike | null): PanelWidths {
  if (!storage) return { ...DEFAULT_PANEL_WIDTHS };

  try {
    const value = JSON.parse(
      storage.getItem(PANEL_STORAGE_KEY) ?? "null",
    ) as Partial<PanelWidths> | null;
    const widths = { ...DEFAULT_PANEL_WIDTHS };

    for (const id of Object.keys(PANEL_SPECS) as PanelId[]) {
      const candidate = value?.[id];
      if (typeof candidate === "number" && Number.isFinite(candidate)) {
        widths[id] = Math.min(
          PANEL_SPECS[id].max,
          Math.max(PANEL_SPECS[id].min, Math.round(candidate)),
        );
      }
    }
    return widths;
  } catch {
    return { ...DEFAULT_PANEL_WIDTHS };
  }
}

export function writePanelWidths(
  storage: StorageLike | null | undefined,
  widths: PanelWidths,
): void {
  if (!storage) return;

  try {
    storage.setItem(PANEL_STORAGE_KEY, JSON.stringify(widths));
  } catch {
    // Storage is best-effort and may be disabled by the browser.
  }
}
