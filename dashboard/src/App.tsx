import { ReactFlowProvider } from "@xyflow/react";
import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type CSSProperties,
  type KeyboardEvent,
} from "react";

import Canvas from "./components/Canvas";
import Drawer from "./components/Drawer";
import ArticleView from "./components/ArticleView";
import Legend from "./components/Legend";
import NavigationCoordinator from "./components/NavigationCoordinator";
import PanelResizer from "./components/PanelResizer";
import PlayerBar from "./components/PlayerBar";
import Sidebar from "./components/Sidebar";
import TopBar from "./components/TopBar";
import TourOverlay, {
  hasNavigableTourStep,
  type TourSourceStep,
} from "./components/TourOverlay";
import { usePanelWidths } from "./components/usePanelWidths";
import { KE_DATA } from "./data.gen";
import type { LearnStep } from "./lib/learnPath";
import {
  RESIZER_SPACE,
  clampPanelWidth,
  panelBounds,
  resolveExplorePanelWidths,
} from "./lib/panelSizing";
import { useApp, type LayoutPhase, type Mode } from "./store";
import type { KENode } from "./types";

const DRAWER_NODES = KE_DATA.nodes as KENode[];
const DRAWER_NODE_IDS = new Set(DRAWER_NODES.map((node) => node.id));

export function drawerAnnouncementFor(selected: string | null) {
  if (!selected) return "";
  const node = DRAWER_NODES.find((candidate) => candidate.id === selected);
  return node
    ? `${node.label} selected. Explanation opened.`
    : "Selected item is unavailable.";
}

export type DrawerAnnouncementState = {
  message: string;
  revision: number;
};

export function nextDrawerAnnouncement(
  current: DrawerAnnouncementState,
  selected: string | null,
): DrawerAnnouncementState {
  const message = drawerAnnouncementFor(selected);
  if (!message) {
    return current.message ? { ...current, message: "" } : current;
  }
  return { message, revision: current.revision + 1 };
}

export function getDrawerLifecycleAction({
  wasOpen,
  isOpen,
  wasModalOpen,
  isModalOpen,
  previousSelected,
  selected,
}: {
  wasOpen: boolean;
  isOpen: boolean;
  wasModalOpen: boolean;
  isModalOpen: boolean;
  previousSelected: string | null;
  selected: string | null;
}) {
  const origin = !wasOpen && isOpen
    ? "capture"
    : wasOpen && !isOpen
      ? "restore"
      : null;
  const focus = isModalOpen
    ? !wasModalOpen
      ? "close"
      : selected !== previousSelected
        ? "heading"
        : null
    : null;
  return { origin, focus };
}

export type EscapeLayer = "sidebar" | "drawer" | "tour" | null;

export function getEscapeLayer({
  drawerModalOpen,
  drawerOpen,
  sidebarModalOpen,
  tourVisible,
}: {
  drawerModalOpen: boolean;
  drawerOpen: boolean;
  sidebarModalOpen: boolean;
  tourVisible: boolean;
}): EscapeLayer {
  if (drawerModalOpen) return "drawer";
  if (sidebarModalOpen) return "sidebar";
  if (tourVisible) return "tour";
  return drawerOpen ? "drawer" : null;
}

export function tourIsVisible({
  dismissed,
  mode,
  nodeIds,
  tour,
}: {
  dismissed: boolean;
  mode: Mode;
  nodeIds: Set<string>;
  tour: Pick<TourSourceStep, "nodeIds">[];
}) {
  if (mode !== "explore") return false;
  return !dismissed && hasNavigableTourStep(tour, nodeIds);
}

export function autoStartStep({ mode, layoutPhase, learnIdx, selected, steps }: {
  mode: Mode;
  layoutPhase: LayoutPhase;
  learnIdx: number | null;
  selected: string | null;
  steps: LearnStep[];
}): { index: number; nodeId: string } | null {
  if (mode !== "learn" || layoutPhase !== "ready") return null;
  if (learnIdx !== null || selected !== null || steps.length === 0) return null;
  return { index: 0, nodeId: steps[0].nodeId };
}

function useNarrowViewport() {
  const [narrow, setNarrow] = useState(() => (
    typeof window !== "undefined"
      && window.matchMedia("(max-width: 899px)").matches
  ));

  useEffect(() => {
    const query = window.matchMedia("(max-width: 899px)");
    const update = () => setNarrow(query.matches);
    update();
    query.addEventListener("change", update);
    return () => query.removeEventListener("change", update);
  }, []);

  return narrow;
}

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const narrow = useNarrowViewport();
  const panels = usePanelWidths();
  const selected = useApp((state) => state.selected);
  const setSelected = useApp((state) => state.setSelected);
  const tourDismissed = useApp((state) => state.tourDismissed);
  const mode = useApp((state) => state.mode);
  const selectedNode = DRAWER_NODES.find((node) => node.id === selected);
  const [drawerStatus, setDrawerStatus] = useState<DrawerAnnouncementState>(
    () => nextDrawerAnnouncement({ message: "", revision: 0 }, selected),
  );
  const drawerOpen = selected !== null;
  const drawerModalOpen = narrow && drawerOpen;
  const sidebarModalOpen = narrow && sidebarOpen && !drawerModalOpen;
  const tourVisible = tourIsVisible({
    dismissed: tourDismissed,
    mode,
    nodeIds: DRAWER_NODE_IDS,
    tour: KE_DATA.tour,
  });
  const escapeLayer = getEscapeLayer({
    drawerModalOpen,
    drawerOpen,
    sidebarModalOpen,
    tourVisible,
  });
  const sidebarRef = useRef<HTMLElement>(null);
  const sidebarTriggerRef = useRef<HTMLButtonElement>(null);
  const drawerRef = useRef<HTMLElement>(null);
  const drawerOriginRef = useRef<HTMLElement | null>(null);
  const drawerWasOpenRef = useRef(false);
  const drawerWasModalRef = useRef(false);
  const drawerPreviousSelectedRef = useRef<string | null>(null);
  const exploreWidths = resolveExplorePanelWidths(
    panels.preferred,
    panels.viewportWidth,
    drawerOpen,
  );
  const drawerInline = drawerOpen && panels.viewportWidth >= 1280;
  const diagnosticsBounds = panelBounds(
    "diagnostics",
    panels.viewportWidth,
    drawerInline ? exploreWidths.explanation + RESIZER_SPACE : 0,
  );
  const explanationBounds = panelBounds(
    "explanation",
    panels.viewportWidth,
    drawerInline ? exploreWidths.diagnostics + RESIZER_SPACE : 0,
  );
  const guidedBounds = panelBounds("guided-rail", panels.viewportWidth);
  const guidedWidth = clampPanelWidth(
    "guided-rail",
    panels.preferred["guided-rail"],
    panels.viewportWidth,
  );
  const shellStyle = {
    "--diagnostics-width": `${exploreWidths.diagnostics}px`,
    "--drawer-width": `${exploreWidths.explanation}px`,
    "--guided-rail-width": `${guidedWidth}px`,
  } as CSSProperties;

  const closeSidebar = useCallback(() => {
    setSidebarOpen(false);
    if (narrow) {
      window.requestAnimationFrame(() => sidebarTriggerRef.current?.focus());
    }
  }, [narrow]);

  // Note: the old learn-mode auto-start effect is gone — learn mode renders
  // ArticleView (no graph navigation); autoStartStep stays exported for its
  // unit tests until fully retired.

  useEffect(() => {
    if (escapeLayer !== "sidebar") return;
    const frame = window.requestAnimationFrame(() => {
      sidebarRef.current
        ?.querySelector<HTMLButtonElement>(".sidebar-sheet-close")
        ?.focus();
    });
    const onEscape = (event: globalThis.KeyboardEvent) => {
      if (event.key === "Escape") closeSidebar();
    };
    window.addEventListener("keydown", onEscape);
    return () => {
      window.cancelAnimationFrame(frame);
      window.removeEventListener("keydown", onEscape);
    };
  }, [closeSidebar, escapeLayer]);

  useEffect(() => {
    if (drawerModalOpen && sidebarOpen) setSidebarOpen(false);
  }, [drawerModalOpen, sidebarOpen]);

  useEffect(() => {
    setDrawerStatus((current) => nextDrawerAnnouncement(current, selected));
    if (!selected || selectedNode) return;
    let clearFrame: number | null = null;
    const announceFrame = window.requestAnimationFrame(() => {
      clearFrame = window.requestAnimationFrame(() => setSelected(null));
    });
    return () => {
      window.cancelAnimationFrame(announceFrame);
      if (clearFrame !== null) window.cancelAnimationFrame(clearFrame);
    };
  }, [selected, selectedNode, setSelected]);

  useEffect(() => {
    const action = getDrawerLifecycleAction({
      wasOpen: drawerWasOpenRef.current,
      isOpen: drawerOpen,
      wasModalOpen: drawerWasModalRef.current,
      isModalOpen: drawerModalOpen,
      previousSelected: drawerPreviousSelectedRef.current,
      selected,
    });
    let frame: number | null = null;

    if (action.origin === "capture") {
      const active = document.activeElement instanceof HTMLElement
        ? document.activeElement
        : null;
      drawerOriginRef.current = active && sidebarRef.current?.contains(active)
        ? sidebarTriggerRef.current
        : active;
    } else if (action.origin === "restore") {
      const returnTarget = drawerOriginRef.current;
      drawerOriginRef.current = null;
      frame = window.requestAnimationFrame(() => returnTarget?.focus());
    }

    if (action.focus) {
      const selector = action.focus === "close"
        ? ".drawer-close"
        : ".drawer-title";
      frame = window.requestAnimationFrame(() => {
        drawerRef.current?.querySelector<HTMLElement>(selector)?.focus();
      });
    }

    drawerWasOpenRef.current = drawerOpen;
    drawerWasModalRef.current = drawerModalOpen;
    drawerPreviousSelectedRef.current = selected;
    return () => {
      if (frame !== null) window.cancelAnimationFrame(frame);
    };
  }, [drawerModalOpen, drawerOpen, selected]);

  useEffect(() => {
    if (escapeLayer !== "drawer") return;
    const onEscape = (event: globalThis.KeyboardEvent) => {
      if (event.key === "Escape") setSelected(null);
    };
    window.addEventListener("keydown", onEscape);
    return () => window.removeEventListener("keydown", onEscape);
  }, [escapeLayer, setSelected]);

  const trapSidebarFocus = (event: KeyboardEvent<HTMLElement>) => {
    if (!sidebarModalOpen || event.key !== "Tab") return;
    const focusable = Array.from(
      sidebarRef.current?.querySelectorAll<HTMLElement>(
        "button:not(:disabled), input:not(:disabled), [tabindex]:not([tabindex='-1'])",
      ) ?? [],
    ).filter((element) => element.tabIndex >= 0 && element.getClientRects().length > 0);
    if (focusable.length === 0) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  };

  const trapDrawerFocus = (event: KeyboardEvent<HTMLElement>) => {
    if (!drawerModalOpen || event.key !== "Tab") return;
    const focusable = Array.from(
      drawerRef.current?.querySelectorAll<HTMLElement>(
        "button:not(:disabled), a[href], summary, [tabindex]:not([tabindex='-1'])",
      ) ?? [],
    ).filter((element) => element.tabIndex >= 0 && element.getClientRects().length > 0);
    if (focusable.length === 0) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  };

  return (
    <ReactFlowProvider>
      <NavigationCoordinator />
      <p
        aria-atomic="true"
        aria-live="polite"
        className="sr-only"
        id="drawer-live-status"
        role="status"
      >
        <span key={`${drawerOpen ? "open" : "closed"}-${drawerStatus.revision}`}>
          {drawerOpen ? drawerStatus.message : ""}
        </span>
      </p>
      <div className="shell" style={shellStyle}>
        <button
          aria-hidden="true"
          aria-label="Close Insights / Trace"
          className={`sidebar-sheet-backdrop${sidebarModalOpen ? " is-open" : ""}`}
          onClick={closeSidebar}
          tabIndex={-1}
          type="button"
        />
        {mode === "explore" && (
          <aside
            aria-hidden={drawerModalOpen || (narrow && !sidebarOpen) ? true : undefined}
            aria-label="Insights and build trace"
            aria-modal={sidebarModalOpen ? true : undefined}
            className={`sidebar${sidebarOpen ? " sidebar-open" : ""}`}
            id="left-panel"
            inert={drawerModalOpen || (narrow && !sidebarOpen) ? true : undefined}
            onKeyDown={trapSidebarFocus}
            ref={sidebarRef}
            role={narrow ? "dialog" : "complementary"}
          >
            <Sidebar onCloseSheet={closeSidebar} />
          </aside>
        )}
        {mode === "explore" && !narrow && (
          <PanelResizer
            bounds={diagnosticsBounds}
            id="diagnostics"
            label="Resize diagnostics panel"
            onChange={(width) => panels.setWidth("diagnostics", width)}
            onReset={() => panels.resetWidth("diagnostics")}
            side="left"
            value={exploreWidths.diagnostics}
          />
        )}
        <main
          aria-hidden={sidebarModalOpen ? true : undefined}
          className="main"
          inert={sidebarModalOpen ? true : undefined}
        >
          <header
            aria-hidden={drawerModalOpen ? true : undefined}
            className="topbar"
            id="topbar"
            inert={drawerModalOpen ? true : undefined}
          >
            <TopBar
              onOpenSidebar={() => setSidebarOpen(true)}
              sidebarOpen={sidebarOpen}
              sidebarTriggerRef={sidebarTriggerRef}
            />
          </header>
          {mode === "learn" ? (
            <ArticleView
              onRailReset={() => panels.resetWidth("guided-rail")}
              onRailResize={(width) => panels.setWidth("guided-rail", width)}
              railBounds={guidedBounds}
              railWidth={guidedWidth}
              resizable={!narrow}
            />
          ) : (
            <div className={`workspace${drawerOpen ? " drawer-open" : ""}`}>
              <div
                aria-hidden={drawerModalOpen ? true : undefined}
                className="canvas-wrap"
                inert={drawerModalOpen ? true : undefined}
              >
                <Canvas />
                <Legend />
                <PlayerBar />
                <TourOverlay escapeEnabled={escapeLayer === "tour"} />
              </div>
              {drawerModalOpen && (
                <button
                  aria-hidden="true"
                  className="drawer-backdrop"
                  onClick={() => setSelected(null)}
                  tabIndex={-1}
                  type="button"
                />
              )}
              {drawerOpen && !narrow && (
                <PanelResizer
                  bounds={explanationBounds}
                  id="explanation"
                  label="Resize explanation panel"
                  onChange={(width) => panels.setWidth("explanation", width)}
                  onReset={() => panels.resetWidth("explanation")}
                  side="right"
                  value={exploreWidths.explanation}
                />
              )}
              {drawerOpen && (
                <aside
                  aria-label="Explanation drawer"
                  aria-modal={drawerModalOpen ? true : undefined}
                  className="drawer"
                  id="drawer"
                  onKeyDown={trapDrawerFocus}
                  ref={drawerRef}
                  role={drawerModalOpen ? "dialog" : "complementary"}
                >
                  <Drawer />
                </aside>
              )}
            </div>
          )}
        </main>
      </div>
    </ReactFlowProvider>
  );
}
