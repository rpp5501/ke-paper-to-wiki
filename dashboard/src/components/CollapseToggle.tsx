// R16.B1 — fold a node's part-of branch out of the graph. Lives in the
// drawer rather than on the node card: the card is itself a <button>, so a
// nested control would be invalid markup, and a double-click gesture on the
// canvas would leave keyboard users with no way to collapse at all.
import { collapsedCount, hasChildren } from "../lib/collapse";
import { useApp } from "../store";
import type { KEEdge } from "../types";

export type CollapseTogglePresentationProps = {
  collapsed: boolean;
  count: number;
  label: string;
  onToggle: () => void;
};

export function CollapseTogglePresentation({
  collapsed,
  count,
  label,
  onToggle,
}: CollapseTogglePresentationProps) {
  if (count === 0) return null;

  return (
    <button
      aria-pressed={collapsed}
      className="collapse-toggle"
      onClick={onToggle}
      type="button"
    >
      {collapsed
        ? `Expand branch (${count} hidden)`
        : `Collapse branch (${count})`}
      <span className="sr-only"> under {label}</span>
    </button>
  );
}

export default function CollapseToggle({
  edges,
  label,
  nodeId,
}: {
  edges: KEEdge[];
  label: string;
  nodeId: string;
}) {
  const collapsed = useApp((state) => state.collapsed);
  const toggleCollapsed = useApp((state) => state.toggleCollapsed);

  return (
    <CollapseTogglePresentation
      collapsed={collapsed.has(nodeId)}
      count={hasChildren(nodeId, edges) ? collapsedCount(nodeId, edges) : 0}
      label={label}
      onToggle={() => toggleCollapsed(nodeId)}
    />
  );
}
