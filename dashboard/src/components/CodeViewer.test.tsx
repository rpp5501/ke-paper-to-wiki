import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import {
  CodeListingPresentation,
  CodeViewerPresentation,
  calledHelpers,
  nodeHasCode,
} from "./CodeViewer";

describe("CodeViewer", () => {
  it("resolves call edges to available helper nodes", () => {
    expect(calledHelpers(
      "caller",
      [
        { id: "caller", kind: "function", label: "caller" },
        { id: "helper", kind: "function", label: "helper" },
      ],
      [{ src: "caller", dst: "helper", kind: "calls", weight: 1 }],
    ).map((node) => node.id)).toEqual(["helper"]);
  });

  it("renders local Prism tokens as class-based semantic code", () => {
    const markup = renderToStaticMarkup(
      <CodeViewerPresentation
        excerpt={'def attention(query):\n    return query'}
        node={{ id: "attention.py::attention", kind: "function", label: "attention" }}
      />,
    );

    expect(markup).toContain('aria-label="Code excerpt for attention"');
    expect(markup).toContain('class="code-viewer"');
    expect(markup).toContain('class="token keyword"');
    expect(markup).not.toContain("style=");
    expect(markup).toContain("def");
  });

  it("omits non-code kinds and blank excerpts", () => {
    expect(renderToStaticMarkup(
      <CodeViewerPresentation
        excerpt="const value = 1"
        node={{ id: "concept", kind: "concept", label: "Concept" }}
      />,
    )).toBe("");
    expect(renderToStaticMarkup(
      <CodeViewerPresentation
        excerpt="   "
        node={{ id: "route", kind: "route", label: "Route" }}
      />,
    )).toBe("");
  });

  it("drops its own section chrome when embedded in the drawer disclosure", () => {
    const node = {
      id: "attention.py::attention",
      kind: "function",
      label: "attention",
    };
    const excerpt = "def attention(query):\n    return query";

    const standalone = renderToStaticMarkup(
      <CodeViewerPresentation excerpt={excerpt} node={node} />,
    );
    const embedded = renderToStaticMarkup(
      <CodeViewerPresentation embedded excerpt={excerpt} node={node} />,
    );

    expect(standalone).toContain("drawer-code");
    expect(standalone).toContain("Code excerpt</h3>");
    expect(embedded).not.toContain("drawer-code");
    expect(embedded).not.toContain("<h3");
    expect(embedded).toContain('class="code-viewer"');
    expect(embedded).toContain('aria-label="Code excerpt for attention"');
  });

  it("nodeHasCode requires a code-kind node with a non-blank excerpt", () => {
    expect(nodeHasCode({ id: "f", kind: "function", label: "f" }, "def x(): pass")).toBe(true);
    expect(nodeHasCode({ id: "c", kind: "concept", label: "c" }, "code")).toBe(false);
    expect(nodeHasCode({ id: "f", kind: "function", label: "f" }, "   ")).toBe(false);
    expect(nodeHasCode(undefined, "x")).toBe(false);
  });

  it("discloses the preview range and expands to the complete symbol", () => {
    const listing = {
      path: "sid.py",
      language: "python",
      symbolKind: "function" as const,
      startLine: 29,
      endLine: 81,
      previewEndLine: 68,
      preview: "def reachable():\n    first = True",
      full: "def reachable():\n    first = True\n    return complete",
      rangeResolved: true,
    };

    const preview = renderToStaticMarkup(
      <CodeListingPresentation
        expanded={false}
        listing={listing}
        nodeLabel="reachable"
        onToggle={() => {}}
      />,
    );
    expect(preview).toContain("lines 29–68 of 29–81");
    expect(preview).toContain("Show complete function");
    expect(preview).not.toContain("return complete");
    expect(preview).toContain('data-line-number="29"');

    const full = renderToStaticMarkup(
      <CodeListingPresentation
        expanded
        listing={listing}
        nodeLabel="reachable"
        onToggle={() => {}}
      />,
    );
    expect(full).toContain("Hide complete function");
    expect(full).toContain(">return</span>");
    expect(full).toContain(" complete");
    expect(full).toContain('data-line-number="31"');
  });

  it("labels start-only listings as unresolved", () => {
    const markup = renderToStaticMarkup(
      <CodeListingPresentation
        expanded={false}
        listing={{
          path: "unknown.rs",
          language: "rust",
          symbolKind: "function",
          startLine: 10,
          endLine: 49,
          previewEndLine: 49,
          preview: "fn unknown() {}",
          full: "fn unknown() {}",
          rangeResolved: false,
        }}
        nodeLabel="unknown"
        onToggle={() => {}}
      />,
    );

    expect(markup).toContain("range unresolved");
    expect(markup).not.toContain("Show complete");
  });
});
