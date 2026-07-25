// R15.1 — the "Continue" panel: next-step ideas from the next_steps pipeline,
// each anchored to concept nodes. Renders nothing on a build without
// --next-steps. Confirmed ideas arrive pre-sorted first from build_data.
import { useState } from "react";

import { getNextSteps } from "../lib/nextSteps";
import { useNodeNavigation } from "./useNodeNavigation";

const KIND_LABEL: Record<string, string> = {
  "paper-limitation": "limitation",
  "unresolved-note": "open question",
  "no-implements-concept": "build it",
};

export default function ContinuePanel() {
  const [open, setOpen] = useState(false);
  const goToNode = useNodeNavigation();
  const steps = getNextSteps();

  if (steps.length === 0) return null;

  return (
    <div className="continue-panel">
      <button
        aria-expanded={open}
        aria-haspopup="true"
        className="continue-toggle"
        onClick={() => setOpen((value) => !value)}
        type="button"
      >
        Continue ({steps.length})
      </button>
      {open && (
        <ul aria-label="Next steps after this paper" className="continue-list">
          {steps.map((step) => (
            <li key={step.title}>
              <div className="continue-head">
                <span className="continue-title">
                  {step.confirmed ? "★ " : ""}
                  {step.title}
                </span>
                <span className="continue-kind">
                  {KIND_LABEL[step.kind] ?? step.kind}
                </span>
              </div>
              <p className="continue-rationale">{step.rationale}</p>
              <div className="continue-anchors">
                {step.nodes.map((nodeId) => (
                  <button
                    key={nodeId}
                    onClick={() => {
                      goToNode(nodeId);
                      setOpen(false);
                    }}
                    type="button"
                  >
                    {nodeId}
                  </button>
                ))}
                {step.sources.map((source) => (
                  <span className="continue-source" key={source}>{source}</span>
                ))}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
