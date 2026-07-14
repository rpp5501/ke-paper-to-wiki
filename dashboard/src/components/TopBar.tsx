import { useRef, useState, type ChangeEvent, type KeyboardEvent, type Ref } from "react";

import { KE_DATA } from "../data.gen";
import {
  moveIndex,
  navigationDisabledReason,
  resolveSearch,
  type IndexNavigationKey,
} from "../lib/navigation";
import { useApp } from "../store";
import type { KENode } from "../types";
import CompactPill from "./CompactPill";
import { useNodeNavigation } from "./useNodeNavigation";

const VIEWS = ["concepts", "clusters", "code", "bridged"] as const;
const EDGE_KINDS = ["implements", "prerequisite", "builds-on"] as const;
const KE_NODES = KE_DATA.nodes as KENode[];
const VIEW_KEYS = new Set([
  "ArrowLeft",
  "ArrowRight",
  "ArrowUp",
  "ArrowDown",
  "Home",
  "End",
]);

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
    view,
    setView,
    hiddenKinds,
    toggleKind,
    blastOn,
    setBlastOn,
    layoutPhase,
  } = useApp();
  const viewRefs = useRef<Array<HTMLButtonElement | null>>([]);
  const noNodes = KE_NODES.length === 0;

  const onViewKeyDown = (
    event: KeyboardEvent<HTMLButtonElement>,
    index: number,
  ) => {
    if (!VIEW_KEYS.has(event.key)) return;
    event.preventDefault();
    const next = moveIndex(
      index,
      VIEWS.length,
      event.key as IndexNavigationKey,
    );
    setView(VIEWS[next]);
    viewRefs.current[next]?.focus();
  };

  return (
    <>
      <CompactPill
        active={sidebarOpen}
        aria-controls="left-panel"
        aria-expanded={sidebarOpen}
        className="sidebar-sheet-trigger"
        onClick={onOpenSidebar}
        ref={sidebarTriggerRef}
      >
        Open Insights / Trace
      </CompactPill>

      <div aria-label="Graph view" className="topbar-group" role="radiogroup">
        {VIEWS.map((candidate, index) => (
          <CompactPill
            active={view === candidate}
            aria-checked={view === candidate}
            disabled={noNodes}
            id={`graph-view-${candidate}`}
            key={candidate}
            onClick={() => setView(candidate)}
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
              onClick={() => toggleKind(kind)}
            >
              {kind}
            </CompactPill>
          );
        })}
        <CompactPill
          active={blastOn}
          aria-pressed={blastOn}
          disabled={noNodes}
          onClick={() => setBlastOn(!blastOn)}
        >
          blast radius
        </CompactPill>
      </div>

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
          placeholder="search… (Enter)"
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
