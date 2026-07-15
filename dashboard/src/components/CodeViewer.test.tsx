import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { CodeViewerPresentation, nodeHasCode } from "./CodeViewer";

describe("CodeViewer", () => {
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
});
