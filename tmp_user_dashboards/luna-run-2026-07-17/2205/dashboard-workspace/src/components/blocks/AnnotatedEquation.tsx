import katex from "katex";

import type { AnnotatedEqBlock } from "../../lib/contentBlocks";
import { safeKatexOptions } from "../../lib/mathHtml";

function renderTex(tex: string, displayMode: boolean): string {
  try {
    return katex.renderToString(tex, safeKatexOptions(displayMode));
  } catch {
    return tex;
  }
}

export default function AnnotatedEquation({ block }: { block: AnnotatedEqBlock }) {
  return (
    <figure className="annotated-eq">
      <div
        className="annotated-eq-math"
        dangerouslySetInnerHTML={{ __html: renderTex(block.latex, true) }}
      />
      <dl className="eq-legend">
        {block.terms.map((term) => (
          <div className={`eq-legend-row eq-term-${term.role}`} key={term.tex}>
            <dt
              className="eq-legend-tex"
              dangerouslySetInnerHTML={{ __html: renderTex(term.tex, false) }}
            />
            <dd className="eq-legend-words">{term.words}</dd>
          </div>
        ))}
      </dl>
    </figure>
  );
}
