import type { ReactNode } from "react";

import type { ContentSegment } from "../../lib/contentBlocks";
import AlgorithmWalkthrough from "./AlgorithmWalkthrough";
import AnnotatedEquation from "./AnnotatedEquation";
import DerivationSteps from "./DerivationSteps";
import FigurePlaceholder from "./FigurePlaceholder";
import MermaidDiagram from "./MermaidDiagram";

export default function BlockRenderer({
  expandAll = false,
  renderMarkdown,
  segment,
}: {
  expandAll?: boolean;
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
      return <FigurePlaceholder block={segment} />;
    case "mermaid":
      return <MermaidDiagram block={segment} />;
  }
}
