import { Highlight, type Language } from "prism-react-renderer";
import { useState } from "react";

import { KE_DATA } from "../data.gen";
import { useApp } from "../store";
import type { CodeListing, KEEdge, KENode } from "../types";

const CODE_KINDS = new Set(["function", "method", "class", "file", "route"]);
const NODES = KE_DATA.nodes as KENode[];
const EDGES = KE_DATA.edges as KEEdge[];
const EXCERPTS = (
  KE_DATA as typeof KE_DATA & { excerpts?: Record<string, string> }
).excerpts ?? {};
const CODE_LISTINGS = (
  KE_DATA as typeof KE_DATA & { codeListings?: Record<string, CodeListing> }
).codeListings ?? {};

export function calledHelpers(
  nodeId: string,
  nodes: KENode[],
  edges: KEEdge[],
): KENode[] {
  const byId = new Map(nodes.map((node) => [node.id, node]));
  return edges
    .filter((edge) => edge.kind === "calls" && edge.src === nodeId)
    .map((edge) => byId.get(edge.dst))
    .filter((node): node is KENode => Boolean(node && CODE_KINDS.has(node.kind)));
}

function languageFor(node: KENode): Language {
  const source = node.source_ref?.split(":", 1)[0].toLocaleLowerCase() ?? "";
  if (source.endsWith(".ts") || source.endsWith(".tsx")) return "typescript";
  if (source.endsWith(".js") || source.endsWith(".jsx")) return "javascript";
  if (source.endsWith(".json")) return "json";
  if (source.endsWith(".css")) return "css";
  if (source.endsWith(".html")) return "markup";
  if (source.endsWith(".sh")) return "bash";
  return "python";
}

function listingLanguage(listing: CodeListing): Language {
  const known = new Set([
    "python", "typescript", "javascript", "json", "css", "markup", "bash",
  ]);
  return (known.has(listing.language) ? listing.language : "python") as Language;
}

function HighlightedCode({
  code,
  language,
  nodeLabel,
  startLine = 1,
}: {
  code: string;
  language: Language;
  nodeLabel: string;
  startLine?: number;
}) {
  return (
    <Highlight code={code} language={language}>
      {({ tokens }) => (
        <pre className="code-viewer">
          <code aria-label={`Code excerpt for ${nodeLabel}`}>
            {tokens.map((line, lineIndex) => (
              <span
                className="code-line"
                data-line-number={startLine + lineIndex}
                key={lineIndex}
              >
                <span aria-hidden="true" className="code-line-number">
                  {startLine + lineIndex}
                </span>
                <span className="code-line-source">
                  {line.map((token, tokenIndex) => (
                    <span
                      className={["token", ...token.types].join(" ")}
                      key={tokenIndex}
                    >
                      {token.content}
                    </span>
                  ))}
                </span>
                {lineIndex < tokens.length - 1 ? "\n" : null}
              </span>
            ))}
          </code>
        </pre>
      )}
    </Highlight>
  );
}

export function nodeHasCode(
  node: KENode | undefined,
  excerpt: string | undefined,
): excerpt is string {
  return !!node && CODE_KINDS.has(node.kind) && !!excerpt?.trim();
}

export function hasCodeFor(nodeId: string): boolean {
  if (CODE_LISTINGS[nodeId]?.preview.trim()) return true;
  return nodeHasCode(
    NODES.find((candidate) => candidate.id === nodeId),
    EXCERPTS[nodeId],
  );
}


export function CodeListingPresentation({
  expanded,
  listing,
  nodeLabel,
  onCopy,
  onToggle,
}: {
  expanded: boolean;
  listing: CodeListing;
  nodeLabel: string;
  onCopy?: () => void;
  onToggle: () => void;
}) {
  const canExpand = listing.rangeResolved && listing.full !== listing.preview;
  const code = expanded && canExpand ? listing.full : listing.preview;
  const visibleEnd = expanded && canExpand
    ? listing.endLine
    : listing.previewEndLine;
  const range = listing.rangeResolved
    ? `lines ${listing.startLine}–${visibleEnd} of ${listing.startLine}–${listing.endLine}`
    : `starts at line ${listing.startLine} · range unresolved`;

  return (
    <div className="code-listing">
      <div className="code-listing-toolbar">
        <span className="code-listing-range">{listing.path} · {range}</span>
        <div className="code-listing-actions">
          {onCopy && (
            <button onClick={onCopy} type="button">Copy complete symbol</button>
          )}
          {canExpand && (
            <button aria-expanded={expanded} onClick={onToggle} type="button">
              {expanded ? "Hide" : "Show"} complete {listing.symbolKind}
            </button>
          )}
        </div>
      </div>
      <HighlightedCode
        code={code}
        language={listingLanguage(listing)}
        nodeLabel={nodeLabel}
        startLine={listing.startLine}
      />
    </div>
  );
}

function CodeListingViewer({ listing, nodeLabel }: {
  listing: CodeListing;
  nodeLabel: string;
}) {
  const [expanded, setExpanded] = useState(false);
  const copy = typeof navigator !== "undefined" && navigator.clipboard
    ? () => { void navigator.clipboard.writeText(listing.full); }
    : undefined;
  return (
    <CodeListingPresentation
      expanded={expanded}
      listing={listing}
      nodeLabel={nodeLabel}
      onCopy={copy}
      onToggle={() => setExpanded((current) => !current)}
    />
  );
}

export function CodeViewerPresentation({
  excerpt,
  listing,
  node,
  embedded = false,
}: {
  excerpt: string | undefined;
  listing?: CodeListing;
  node: KENode;
  embedded?: boolean;
}) {
  if (!listing && !nodeHasCode(node, excerpt)) return null;

  const rendered = listing ? (
    <CodeListingViewer listing={listing} nodeLabel={node.label} />
  ) : (
    <HighlightedCode
      code={excerpt ?? ""}
      language={languageFor(node)}
      nodeLabel={node.label}
    />
  );

  // Embedded inside the drawer's "See it in code" disclosure, which already
  // supplies the section chrome and heading.
  if (embedded) return rendered;

  return (
    <section aria-labelledby="drawer-code-heading" className="drawer-section drawer-code">
      <h3 id="drawer-code-heading">Code excerpt</h3>
      {rendered}
    </section>
  );
}

export default function CodeViewer({
  nodeId,
  embedded = false,
}: {
  nodeId: string;
  embedded?: boolean;
}) {
  const setSelected = useApp((state) => state.setSelected);
  const node = NODES.find((candidate) => candidate.id === nodeId);
  if (!node) return null;
  const helpers = calledHelpers(nodeId, NODES, EDGES);
  return (
    <>
      <CodeViewerPresentation
        embedded={embedded}
        excerpt={EXCERPTS[nodeId]}
        listing={CODE_LISTINGS[nodeId]}
        node={node}
      />
      {helpers.length > 0 && (
        <div className="code-helper-links">
          <span>Calls</span>
          {helpers.map((helper) => (
            <button
              key={helper.id}
              onClick={() => setSelected(helper.id)}
              type="button"
            >
              {helper.label}
            </button>
          ))}
        </div>
      )}
    </>
  );
}
