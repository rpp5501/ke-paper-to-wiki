import { useRef, useState, type ChangeEvent, type KeyboardEvent, type Ref } from "react";

import { KE_DATA } from "../data.gen";
import {
  moveIndex,
  navigationDisabledReason,
  resolveSearch,
  type IndexNavigationKey,
} from "../lib/navigation";
import { useApp, type LayoutPhase, type Mode } from "../store";
import type { KENode } from "../types";
import CompactPill from "./CompactPill";
import { useNodeNavigation } from "./useNodeNavigation";

const VIEWS = ["concepts", "clusters", "code", "bridged"] as const;
const EDGE_KINDS = ["implements", "prerequisite", "builds-on"] as const;
const MODES = [
  ["learn", "Guided"],
  ["explore", "Explore"],
] as const;
const KE_NODES = KE_DATA.nodes as KENode[];
const VIEW_KEYS = new Set([
  "ArrowLeft",
  "ArrowRight",
  "ArrowUp",
  "ArrowDown",
  "Home",
  "End",
]);

function rovingKeyDownHandler(
  refs: { current: Array<HTMLButtonElement | null> },
  length: number,
  onSelect: (nextIndex: number) => void,
) {
  return (event: KeyboardEvent<HTMLButtonElement>, index: number) => {
    if (!VIEW_KEYS.has(event.key)) return;
    event.preventDefault();
    const next = moveIndex(index, length, event.key as IndexNavigationKey);
    onSelect(next);
    refs.current[next]?.focus();
  };
}

export type TopBarPresentationProps = {
  blastOn: boolean;
  hiddenKinds: Set<string>;
  layoutPhase: LayoutPhase;
  mode: Mode;
  noNodes: boolean;
  onOpenSidebar: () => void;
  onSetBlastOn: (blastOn: boolean) => void;
  onSetMode: (mode: Mode) => void;
  onSetView: (view: (typeof VIEWS)[number]) => void;
  onToggleKind: (kind: string) => void;
  sidebarOpen: boolean;
  sidebarTriggerRef: Ref<HTMLButtonElement>;
  view: (typeof VIEWS)[number];
};

export function TopBarPresentation({
  blastOn,
  hiddenKinds,
  layoutPhase,
  mode,
  noNodes,
  onOpenSidebar,
  onSetBlastOn,
  onSetMode,
  onSetView,
  onToggleKind,
  sidebarOpen,
  sidebarTriggerRef,
  view,
}: TopBarPresentationProps) {
  const viewRefs = useRef<Array<HTMLButtonElement | null>>([]);
  const modeRefs = useRef<Array<HTMLButtonElement | null>>([]);

  const onViewKeyDown = rovingKeyDownHandler(
    viewRefs,
    VIEWS.length,
    (next) => onSetView(VIEWS[next]),
  );
  const onModeKeyDown = rovingKeyDownHandler(
    modeRefs,
    MODES.length,
    (next) => onSetMode(MODES[next][0]),
  );

  return (
    <>
      <div aria-label="Dashboard mode" className="topbar-group mode-switch" role="radiogroup">
        {MODES.map(([value, label], index) => (
          <CompactPill
            active={mode === value}
            aria-checked={mode === value}
            key={value}
            onClick={() => onSetMode(value)}
            onKeyDown={(event) => onModeKeyDown(event, index)}
            ref={(node) => {
              modeRefs.current[index] = node;
            }}
            role="radio"
            tabIndex={mode === value ? 0 : -1}
          >
            {label}
          </CompactPill>
        ))}
      </div>

      {mode === "explore" && (
        <>
          <CompactPill
            active={sidebarOpen}
            aria-controls="left-panel"
            aria-expanded={sidebarOpen}
            className="sidebar-sheet-trigger"
            onClick={onOpenSidebar}
            ref={sidebarTriggerRef}
          >
            Diagnostics
          </CompactPill>

          <div aria-label="Graph view" className="topbar-group" role="radiogroup">
            {VIEWS.map((candidate, index) => (
              <CompactPill
                active={view === candidate}
                aria-checked={view === candidate}
                disabled={noNodes}
                id={`graph-view-${candidate}`}
                key={candidate}
                onClick={() => onSetView(candidate)}
                onKeyDown={(event) => onViewKeyDown(event, index)}
                ref={(node) => {
                  viewRefs.current[index] = node;
                }}
                role="radio"
                tabIndex={view === candidate ? 0 : -1}
              >
                {candidate}
              </CompactPill>
            ))}
          </div>

          <span aria-hidden="true" className="topbar-separator" />

          <div aria-label="Graph filters" className="topbar-group" role="group">
            {EDGE_KINDS.map((kind) => {
              const visible = !hiddenKinds.has(kind);
              return (
                <CompactPill
                  active={visible}
                  aria-pressed={visible}
                  disabled={noNodes}
                  key={kind}
                  onClick={() => onToggleKind(kind)}
                >
                  {kind}
                </CompactPill>
              );
            })}
            <CompactPill
              active={blastOn}
              aria-pressed={blastOn}
              disabled={noNodes}
              onClick={() => onSetBlastOn(!blastOn)}
              title="Highlight everything that depends on the selected node"
            >
              impact radius
            </CompactPill>
          </div>
        </>
      )}

      {mode === "learn" && (
        <CompactPill
          active={sidebarOpen}
          aria-controls="left-panel"
          aria-expanded={sidebarOpen}
          className="sidebar-sheet-trigger"
          onClick={onOpenSidebar}
          ref={sidebarTriggerRef}
        >
          Learning path
        </CompactPill>
      )}

      <SearchBox
        disabledReason={navigationDisabledReason(
          noNodes ? "empty" : layoutPhase,
          true,
        )}
        view={view}
      />
    </>
  );
}

type TopBarProps = {
  onOpenSidebar: () => void;
  sidebarOpen: boolean;
  sidebarTriggerRef: Ref<HTMLButtonElement>;
};

export default function TopBar({
  onOpenSidebar,
  sidebarOpen,
  sidebarTriggerRef,
}: TopBarProps) {
  const {
    mode,
    setMode,
    view,
    setView,
    hiddenKinds,
    toggleKind,
    blastOn,
    setBlastOn,
    layoutPhase,
  } = useApp();
  const noNodes = KE_NODES.length === 0;

  return (
    <TopBarPresentation
      blastOn={blastOn}
      hiddenKinds={hiddenKinds}
      layoutPhase={layoutPhase}
      mode={mode}
      noNodes={noNodes}
      onOpenSidebar={onOpenSidebar}
      onSetBlastOn={setBlastOn}
      onSetMode={setMode}
      onSetView={setView}
      onToggleKind={toggleKind}
      sidebarOpen={sidebarOpen}
      sidebarTriggerRef={sidebarTriggerRef}
      view={view}
    />
  );
}

function SearchBox({
  disabledReason,
  view,
}: {
  disabledReason: string | null;
  view: typeof VIEWS[number];
}) {
  const navigateToNode = useNodeNavigation();
  const [message, setMessage] = useState("");
  const describedBy = [
    message ? "search-status" : "",
    disabledReason ? "search-disabled-reason" : "",
  ].filter(Boolean).join(" ") || undefined;

  const clearMessage = (_event: ChangeEvent<HTMLInputElement>) => {
    if (message) setMessage("");
  };

  return (
    <div className="search-group">
      <span className="search-field">
        <input
          aria-describedby={describedBy}
          aria-label="Search graph nodes"
          className="search-input"
          disabled={disabledReason !== null}
          onChange={clearMessage}
          onKeyDown={(event) => {
            if (event.key !== "Enter") return;
            const match = resolveSearch(KE_NODES, event.currentTarget.value, view);
            if (!match) {
              setMessage("No matching node");
              return;
            }
            setMessage("");
            navigateToNode(match.nodeId, match.view);
          }}
          placeholder="Find a concept… (Enter)"
          title={disabledReason ?? undefined}
          type="search"
        />
      </span>
      {disabledReason && (
        <span className="sr-only" id="search-disabled-reason">
          {disabledReason}
        </span>
      )}
      <span
        aria-atomic="true"
        aria-live="polite"
        className="search-status"
        id="search-status"
        role="status"
      >
        {message}
      </span>
    </div>
  );
}
