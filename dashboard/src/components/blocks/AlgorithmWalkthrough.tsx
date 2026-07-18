import { useState } from "react";

import type { AlgorithmBlock } from "../../lib/contentBlocks";

function AlgorithmLine({
  code,
  expandAll,
  intent,
}: {
  code: string;
  expandAll: boolean;
  intent: string;
}) {
  const [open, setOpen] = useState(false);
  const expanded = expandAll || open;
  return (
    <li className="algo-line">
      <div className="algo-line-head">
        <code className="algo-code">{code}</code>
        {!expandAll && (
          <button
            aria-expanded={expanded}
            aria-label={`Why: ${code}`}
            className="algo-why-toggle"
            onClick={() => setOpen((current) => !current)}
            type="button"
          >
            {expanded ? "−" : "?"}
          </button>
        )}
      </div>
      {expanded && <p className="algo-intent">{intent}</p>}
    </li>
  );
}

export default function AlgorithmWalkthrough({
  block,
  expandAll = false,
}: {
  block: AlgorithmBlock;
  expandAll?: boolean;
}) {
  return (
    <div className="algo">
      {block.title && <p className="algo-title">{block.title}</p>}
      <ol className="algo-lines">
        {block.lines.map((line, index) => (
          <AlgorithmLine
            code={line.code}
            expandAll={expandAll}
            intent={line.intent}
            key={index}
          />
        ))}
      </ol>
    </div>
  );
}
