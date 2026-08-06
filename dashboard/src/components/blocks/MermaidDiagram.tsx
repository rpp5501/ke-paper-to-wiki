// Renders a ```mermaid fence from a generated page. The mermaid bundle is
// large and most readers never scroll to a diagram, so it is imported lazily
// and shared across every diagram on the page — same reasoning as VizTier's
// deferred iframe mount.
import { useEffect, useRef, useState } from "react";

import type { MermaidBlock } from "../../lib/contentBlocks";

type MermaidApi = {
  initialize: (config: Record<string, unknown>) => void;
  render: (id: string, code: string) => Promise<{ svg: string }>;
};

let pending: Promise<MermaidApi> | null = null;

// Exported so a test can supply a stub instead of loading the real bundle.
export function loadMermaid(): Promise<MermaidApi> {
  pending ??= import("mermaid").then((module) => {
    const api = module.default as unknown as MermaidApi;
    // securityLevel "strict" makes mermaid sanitize its own output, which is
    // what lets the SVG below be injected as HTML.
    api.initialize({ startOnLoad: false, securityLevel: "strict" });
    return api;
  });
  return pending;
}

let counter = 0;

export default function MermaidDiagram({ block }: { block: MermaidBlock }) {
  const [svg, setSvg] = useState<string | null>(null);
  const [failed, setFailed] = useState(false);
  // mermaid needs a DOM-unique id per render; a module counter is enough
  // because ids never outlive the document.
  const idRef = useRef(`mermaid-diagram-${(counter += 1)}`);

  useEffect(() => {
    let cancelled = false;
    setSvg(null);
    setFailed(false);
    loadMermaid()
      .then((mermaid) => mermaid.render(idRef.current, block.code))
      .then((result) => {
        if (!cancelled) setSvg(result.svg);
      })
      .catch(() => {
        if (!cancelled) setFailed(true);
      });
    return () => {
      cancelled = true;
    };
  }, [block.code]);

  // A diagram that will not parse must still show the reader the relationship
  // it encodes, so fall back to the source rather than rendering nothing.
  if (failed) {
    return (
      <figure className="mermaid-diagram mermaid-diagram-failed">
        <pre>{block.code}</pre>
      </figure>
    );
  }

  return (
    <figure className="mermaid-diagram" data-testid="mermaid-diagram">
      {svg === null
        ? <div className="mermaid-diagram-pending" aria-hidden="true" />
        : <div dangerouslySetInnerHTML={{ __html: svg }} />}
    </figure>
  );
}
