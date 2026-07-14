import { Highlight, type Language } from "prism-react-renderer";

import { KE_DATA } from "../data.gen";
import type { KENode } from "../types";

const CODE_KINDS = new Set(["function", "class", "file", "route"]);
const NODES = KE_DATA.nodes as KENode[];
const EXCERPTS = (
  KE_DATA as typeof KE_DATA & { excerpts?: Record<string, string> }
).excerpts ?? {};

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

export function CodeViewerPresentation({
  excerpt,
  node,
}: {
  excerpt: string | undefined;
  node: KENode;
}) {
  if (!CODE_KINDS.has(node.kind) || !excerpt?.trim()) return null;

  return (
    <section aria-labelledby="drawer-code-heading" className="drawer-section drawer-code">
      <h3 id="drawer-code-heading">Code excerpt</h3>
      <Highlight code={excerpt} language={languageFor(node)}>
        {({ tokens }) => (
          <pre className="code-viewer">
            <code aria-label={`Code excerpt for ${node.label}`}>
              {tokens.map((line, lineIndex) => (
                <span className="code-line" key={lineIndex}>
                  {line.map((token, tokenIndex) => (
                    <span
                      className={["token", ...token.types].join(" ")}
                      key={tokenIndex}
                    >
                      {token.content}
                    </span>
                  ))}
                  {lineIndex < tokens.length - 1 ? "\n" : null}
                </span>
              ))}
            </code>
          </pre>
        )}
      </Highlight>
    </section>
  );
}

export default function CodeViewer({ nodeId }: { nodeId: string }) {
  const node = NODES.find((candidate) => candidate.id === nodeId);
  if (!node) return null;
  return <CodeViewerPresentation excerpt={EXCERPTS[nodeId]} node={node} />;
}
