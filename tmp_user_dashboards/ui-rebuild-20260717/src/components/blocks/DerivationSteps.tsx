import katex from "katex";

import type { DerivationBlock } from "../../lib/contentBlocks";
import { safeKatexOptions } from "../../lib/mathHtml";

function renderTex(tex: string): string {
  try {
    return katex.renderToString(tex, safeKatexOptions(true));
  } catch {
    return tex;
  }
}

export default function DerivationSteps({ block }: { block: DerivationBlock }) {
  return (
    <div className="derivation">
      {block.shape && <p className="derivation-shape">{block.shape}</p>}
      <ol className="derivation-steps">
        {block.steps.map((step, index) => (
          <li className="derivation-step" key={index}>
            <div
              className="derivation-latex"
              dangerouslySetInnerHTML={{ __html: renderTex(step.latex) }}
            />
            <p className="derivation-why">{step.why}</p>
          </li>
        ))}
      </ol>
    </div>
  );
}
