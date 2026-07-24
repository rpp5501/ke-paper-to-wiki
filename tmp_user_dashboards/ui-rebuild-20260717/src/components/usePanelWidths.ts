import { useCallback, useEffect, useState } from "react";

import {
  PANEL_SPECS,
  readPanelWidths,
  writePanelWidths,
  type PanelId,
  type PanelWidths,
} from "../lib/panelSizing";

function browserStorage(): Storage | null {
  if (typeof window === "undefined") return null;
  try {
    return window.localStorage;
  } catch {
    return null;
  }
}

export function usePanelWidths() {
  const [preferred, setPreferred] = useState<PanelWidths>(() => (
    readPanelWidths(browserStorage())
  ));
  const [viewportWidth, setViewportWidth] = useState(() => (
    typeof window === "undefined" ? 1440 : window.innerWidth
  ));

  useEffect(() => {
    const update = () => setViewportWidth(window.innerWidth);
    window.addEventListener("resize", update);
    return () => window.removeEventListener("resize", update);
  }, []);

  const setWidth = useCallback((id: PanelId, width: number) => {
    setPreferred((current) => {
      const next = { ...current, [id]: Math.round(width) };
      writePanelWidths(browserStorage(), next);
      return next;
    });
  }, []);

  const resetWidth = useCallback((id: PanelId) => {
    setWidth(id, PANEL_SPECS[id].defaultWidth);
  }, [setWidth]);

  return { preferred, viewportWidth, setWidth, resetWidth };
}
