import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { CodeViewerPresentation } from "./CodeViewer";

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
});
