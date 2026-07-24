// R13 — the Visuals gallery: an index over per-node explorables.
// Renders nothing on a viz-free build. Clicking an item navigates to the
// node (existing NavigationCoordinator path) and asks its Visualize tier
// to open via store.vizFocus.
import { useState } from "react";

import { getVizMap } from "../lib/viz";
import { useApp } from "../store";

export default function VizGallery() {
  const [open, setOpen] = useState(false);
  const openVisualization = useApp((state) => state.openVisualization);
  const entries = Object.entries(getVizMap());

  if (entries.length === 0) return null;

  return (
    <div className="viz-gallery">
      <button
        aria-expanded={open}
        aria-haspopup="true"
        className="viz-gallery-toggle"
        onClick={() => setOpen((value) => !value)}
        type="button"
      >
        Visuals ({entries.length})
      </button>
      {open && (
        <ul aria-label="Interactive visuals" className="viz-gallery-panel">
          {entries.map(([nodeId, entry]) => (
            <li key={nodeId}>
              <button
                onClick={() => {
                  openVisualization(nodeId);
                  setOpen(false);
                }}
                type="button"
              >
                <span className="viz-gallery-title">{entry.title}</span>
                <span className="viz-gallery-caption">{entry.caption}</span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
