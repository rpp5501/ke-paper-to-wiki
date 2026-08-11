import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import PaperFigure from "./PaperFigure";

const FIGURES = {
  fig_1: {
    caption: "The Transformer - model architecture.",
    section: "sec_3",
    images: ["figures/arXiv-1706.03762/Figures/ModalNet-21.png"],
  },
  fig_2: {
    caption: "(left) Scaled Dot-Product Attention. (right) Multi-Head Attention.",
    section: "sec_3_2_2",
    images: ["figures/x/a.png", "figures/x/b.png"],
  },
  fig_3: { caption: "A TikZ drawing.", section: "sec_8", images: [] },
};

describe("PaperFigure", () => {
  it("shows the paper's own image", () => {
    const html = renderToStaticMarkup(
      <PaperFigure block={{ type: "figure", id: "fig_1" }} figures={FIGURES} />,
    );

    expect(html).toContain("figures/arXiv-1706.03762/Figures/ModalNet-21.png");
    expect(html).toContain("The Transformer - model architecture.");
  });

  it("renders every panel of a multi-part figure", () => {
    const html = renderToStaticMarkup(
      <PaperFigure block={{ type: "figure", id: "fig_2" }} figures={FIGURES} />,
    );

    expect(html).toContain("figures/x/a.png");
    expect(html).toContain("figures/x/b.png");
  });

  it("uses the caption as alt text so the figure is not silent to a screen reader", () => {
    const html = renderToStaticMarkup(
      <PaperFigure block={{ type: "figure", id: "fig_1" }} figures={FIGURES} />,
    );

    expect(html).toMatch(/alt="[^"]*Transformer[^"]*"/);
  });

  it("loads lazily, because a page can carry several megabytes of figures", () => {
    const html = renderToStaticMarkup(
      <PaperFigure block={{ type: "figure", id: "fig_1" }} figures={FIGURES} />,
    );

    expect(html).toContain('loading="lazy"');
  });

  it("keeps the caption when the figure has no image to show", () => {
    const html = renderToStaticMarkup(
      <PaperFigure block={{ type: "figure", id: "fig_3" }} figures={FIGURES} />,
    );

    expect(html).toContain("A TikZ drawing.");
    expect(html).not.toContain("<img");
  });

  it("prefers the page's own caption over the pack's when the writer wrote one", () => {
    const html = renderToStaticMarkup(
      <PaperFigure
        block={{ type: "figure", id: "fig_1", caption: "How the blocks stack." }}
        figures={FIGURES}
      />,
    );

    expect(html).toContain("How the blocks stack.");
  });

  it("falls back to the placeholder for an id the pack does not know", () => {
    const html = renderToStaticMarkup(
      <PaperFigure block={{ type: "figure", id: "fig_99" }} figures={FIGURES} />,
    );

    expect(html).not.toContain("<img");
    expect(html).toContain("fig_99");
  });

  it("survives a bundle built before figures existed", () => {
    const html = renderToStaticMarkup(
      <PaperFigure block={{ type: "figure", id: "fig_1" }} figures={undefined} />,
    );

    expect(html).not.toContain("<img");
  });
});
