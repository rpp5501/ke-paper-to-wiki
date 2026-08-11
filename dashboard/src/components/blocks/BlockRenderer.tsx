import type { ReactNode } from "react";

import { KE_DATA } from "../../data.gen";
import type { ContentSegment } from "../../lib/contentBlocks";
import AlgorithmWalkthrough from "./AlgorithmWalkthrough";
import AnnotatedEquation from "./AnnotatedEquation";
import DerivationSteps from "./DerivationSteps";
import MermaidDiagram from "./MermaidDiagram";
import PaperFigure, { type PaperFigures } from "./PaperFigure";

// The pack's recovered figures. Read here rather than inside PaperFigure so
// that component stays a pure function of its props.
const BUNDLE_FIGURES = (KE_DATA as { figures?: PaperFigures }).figures;

export default function BlockRenderer({
  expandAll = false,
  figures = BUNDLE_FIGURES,
  renderMarkdown,
  segment,
}: {
  expandAll?: boolean;
  figures?: PaperFigures;
  renderMarkdown: (markdown: string) => ReactNode;
  segment: ContentSegment;
}) {
  switch (segment.type) {
    case "markdown":
      return <>{renderMarkdown(segment.markdown)}</>;
    case "annotated-eq":
      return <AnnotatedEquation block={segment} />;
    case "derivation":
      return <DerivationSteps block={segment} />;
    case "algorithm":
      return <AlgorithmWalkthrough block={segment} expandAll={expandAll} />;
    case "figure":
      return <PaperFigure block={segment} figures={figures} />;
    case "mermaid":
      return <MermaidDiagram block={segment} />;
  }
}
