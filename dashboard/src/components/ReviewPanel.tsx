// R16.A3 — the review queue: nodes whose evidence just broke or has gone
// stale. Client-side date math only, no scheduler and no notifications;
// scripts/quiz_to_anki.py remains the heavy-SRS path. Renders nothing until
// there is something to review.
import { useState } from "react";

import { reviewQueue } from "../lib/mastery";
import { useApp } from "../store";
import { useNodeNavigation } from "./useNodeNavigation";

export type ReviewPanelPresentationProps = {
  open: boolean;
  queue: string[];
  onToggle: () => void;
  onPick: (nodeId: string) => void;
};

export function ReviewPanelPresentation({
  open,
  queue,
  onToggle,
  onPick,
}: ReviewPanelPresentationProps) {
  if (queue.length === 0) return null;

  return (
    <div className="review-panel">
      <button
        aria-expanded={open}
        aria-haspopup="true"
        className="review-toggle"
        onClick={onToggle}
        type="button"
      >
        Review ({queue.length})
      </button>
      {open && (
        <div className="review-pop">
          <p className="review-hint" role="status">
            Worth another pass
          </p>
          <ul aria-label="Nodes to review" className="review-list">
            {queue.map((nodeId) => (
              <li key={nodeId}>
                <button
                  className="review-node"
                  onClick={() => onPick(nodeId)}
                  type="button"
                >
                  {nodeId}
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default function ReviewPanel() {
  const [open, setOpen] = useState(false);
  const mastery = useApp((state) => state.mastery);
  const setQuizOpen = useApp((state) => state.setQuizOpen);
  const goToNode = useNodeNavigation();
  const queue = reviewQueue(mastery);

  return (
    <ReviewPanelPresentation
      onPick={(nodeId) => {
        goToNode(nodeId);
        setOpen(false);
        setQuizOpen(true);
      }}
      onToggle={() => setOpen((value) => !value)}
      open={open}
      queue={queue}
    />
  );
}
