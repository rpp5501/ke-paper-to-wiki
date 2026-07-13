import { useMemo, useRef, type KeyboardEvent } from "react";

import { KE_DATA } from "../data.gen";
import { computeInsights } from "../lib/insights";
import { moveIndex, type ArrowKey } from "../lib/navigation";
import { useApp } from "../store";
import CompactPill from "./CompactPill";
import { useNodeNavigation } from "./useNodeNavigation";

const TABS = [
  { id: "insights", label: "Insights & Health" },
  { id: "trace", label: "Build Trace" },
] as const;

type SidebarTab = (typeof TABS)[number]["id"];
type TraceEntry = {
  nodeId: string;
  phase: string;
  status: string;
  date: string;
};

type SidebarProps = {
  onCloseSheet: () => void;
};

const NODE_IDS = new Set((KE_DATA.nodes as { id: string }[]).map((node) => node.id));

export default function Sidebar({ onCloseSheet }: SidebarProps) {
  const { sidebarTab, setSidebarTab, selected } = useApp();
  const navigateToNode = useNodeNavigation();
  const insights = useMemo(() => computeInsights(KE_DATA as never), []);
  const trace = KE_DATA.trace as TraceEntry[];
  const tabRefs = useRef<Array<HTMLButtonElement | null>>([]);

  const selectTab = (tab: SidebarTab, index: number) => {
    setSidebarTab(tab);
    tabRefs.current[index]?.focus();
  };

  const onTabKeyDown = (
    event: KeyboardEvent<HTMLButtonElement>,
    index: number,
  ) => {
    if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
    event.preventDefault();
    const next = moveIndex(index, TABS.length, event.key as ArrowKey);
    selectTab(TABS[next].id, next);
  };

  return (
    <div className="sidebar-content">
      <div className="sidebar-sheet-header">
        <span>Insights / Trace</span>
        <CompactPill
          aria-label="Close Insights / Trace"
          className="sidebar-sheet-close"
          onClick={onCloseSheet}
        >
          Close
        </CompactPill>
      </div>

      <div aria-label="Graph diagnostics" className="sidebar-tabs" role="tablist">
        {TABS.map((tab, index) => (
          <CompactPill
            active={sidebarTab === tab.id}
            aria-controls={`${tab.id}-panel`}
            aria-selected={sidebarTab === tab.id}
            id={`${tab.id}-tab`}
            key={tab.id}
            onClick={() => setSidebarTab(tab.id)}
            onKeyDown={(event) => onTabKeyDown(event, index)}
            ref={(node) => {
              tabRefs.current[index] = node;
            }}
            role="tab"
            tabIndex={sidebarTab === tab.id ? 0 : -1}
          >
            {tab.label}
          </CompactPill>
        ))}
      </div>

      <section
        aria-labelledby="insights-tab"
        hidden={sidebarTab !== "insights"}
        id="insights-panel"
        role="tabpanel"
        tabIndex={0}
      >
        {insights.map((insight, index) => (
          <button
            aria-current={selected === insight.nodeId ? "true" : undefined}
            className="card card-button"
            disabled={!NODE_IDS.has(insight.nodeId)}
            key={`${insight.rule}-${insight.nodeId}-${index}`}
            onClick={() => navigateToNode(insight.nodeId)}
            type="button"
          >
            <span className={`sev sev-${insight.severity}`}>
              {insight.severity}
            </span>
            <span className="card-rule">{insight.rule}</span>
            <span className="card-supporting">{insight.text}</span>
          </button>
        ))}
        {insights.length === 0 && (
          <div className="card empty-card">no findings — healthy graph</div>
        )}
      </section>

      <section
        aria-labelledby="trace-tab"
        hidden={sidebarTab !== "trace"}
        id="trace-panel"
        role="tabpanel"
        tabIndex={0}
      >
        {trace.map((entry, index) => (
          <button
            aria-current={selected === entry.nodeId ? "true" : undefined}
            className="card card-button trace-card"
            disabled={!NODE_IDS.has(entry.nodeId)}
            key={`${entry.nodeId}-${entry.phase}-${index}`}
            onClick={() => navigateToNode(entry.nodeId)}
            type="button"
          >
            <strong>{entry.nodeId}</strong> — {entry.phase} [{entry.status}]{" "}
            <span className="trace-date">{entry.date}</span>
          </button>
        ))}
        {trace.length === 0 && (
          <div className="card empty-card">no build trace available</div>
        )}
      </section>
    </div>
  );
}
