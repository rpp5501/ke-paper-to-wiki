import { ReactFlowProvider } from "@xyflow/react";
import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type KeyboardEvent,
} from "react";

import Canvas from "./components/Canvas";
import Legend from "./components/Legend";
import Sidebar from "./components/Sidebar";
import TopBar from "./components/TopBar";

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
  const sidebarRef = useRef<HTMLElement>(null);
  const sidebarTriggerRef = useRef<HTMLButtonElement>(null);

  const closeSidebar = useCallback(() => {
    setSidebarOpen(false);
    if (narrow) {
      window.requestAnimationFrame(() => sidebarTriggerRef.current?.focus());
    }
  }, [narrow]);

  useEffect(() => {
    if (!narrow || !sidebarOpen) return;
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
  }, [closeSidebar, narrow, sidebarOpen]);

  const trapSidebarFocus = (event: KeyboardEvent<HTMLElement>) => {
    if (!narrow || !sidebarOpen || event.key !== "Tab") return;
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

  return (
    <ReactFlowProvider>
      <div className="shell">
        <button
          aria-label="Close Insights / Trace"
          className={`sidebar-sheet-backdrop${sidebarOpen ? " is-open" : ""}`}
          onClick={closeSidebar}
          tabIndex={-1}
          type="button"
        />
        <aside
          aria-hidden={narrow && !sidebarOpen ? true : undefined}
          aria-label="Insights and build trace"
          className={`sidebar${sidebarOpen ? " sidebar-open" : ""}`}
          id="left-panel"
          inert={narrow && !sidebarOpen ? true : undefined}
          onKeyDown={trapSidebarFocus}
          ref={sidebarRef}
        >
          <Sidebar onCloseSheet={closeSidebar} />
        </aside>
        <main className="main">
          <header className="topbar" id="topbar">
            <TopBar
              onOpenSidebar={() => setSidebarOpen(true)}
              sidebarOpen={sidebarOpen}
              sidebarTriggerRef={sidebarTriggerRef}
            />
          </header>
          <div className="workspace">
            <div className="canvas-wrap">
              <Canvas />
              <Legend />
              <div id="playerbar" />
              <div id="tour-overlay" />
            </div>
            <aside className="drawer" id="drawer" />
          </div>
        </main>
      </div>
    </ReactFlowProvider>
  );
}
