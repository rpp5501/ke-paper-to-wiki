import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { deriveBridges } from "./Drawer";
import { CodeViewerPresentation } from "./CodeViewer";
import type { KEEdge } from "../types";

// The shipped AIAYN fixture carries no `implements` edges and no code excerpts,
// so the whole "See it in code" bridge path is unreachable through KE_DATA.
// These tests exercise that path directly with an injected bridge + excerpt.

const IMPLEMENTS: KEEdge[] = [
  { src: "attention.py::attention", dst: "scaled-dot-product-attention", kind: "implements" },
];

describe("deriveBridges", () => {
  it("links a concept to the code node that implements it", () => {
    expect(deriveBridges("scaled-dot-product-attention", IMPLEMENTS)).toEqual([
      { id: "attention.py::attention", relation: "implemented by" },
    ]);
  });

  it("links a code node to the concept it implements", () => {
    expect(deriveBridges("attention.py::attention", IMPLEMENTS)).toEqual([
      { id: "scaled-dot-product-attention", relation: "implements" },
    ]);
  });

  it("returns no bridges for an unrelated node or a null selection", () => {
    expect(deriveBridges("unrelated", IMPLEMENTS)).toEqual([]);
    expect(deriveBridges(null, IMPLEMENTS)).toEqual([]);
  });

  it("ignores non-implements edges", () => {
    const edges: KEEdge[] = [
      { src: "a", dst: "scaled-dot-product-attention", kind: "builds-on" },
    ];
    expect(deriveBridges("scaled-dot-product-attention", edges)).toEqual([]);
  });
});

describe("bridged code excerpt renders", () => {
  it("shows the implementing function's excerpt in the drawer disclosure", () => {
    const markup = renderToStaticMarkup(
      <CodeViewerPresentation
        embedded
        excerpt={"def attention(q, k, v):\n    return softmax(q @ k.T) @ v"}
        node={{ id: "attention.py::attention", kind: "function", label: "attention" }}
      />,
    );
    expect(markup).toContain('aria-label="Code excerpt for attention"');
    expect(markup).toContain("softmax");
  });
});
