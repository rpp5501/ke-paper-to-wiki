import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import {
  activeEquation,
  BridgeButton,
  DrawerPresentation,
  equationHoverValue,
  nextEquationInteraction,
  RichMarkdown,
} from "./Drawer";

const drawerActions = {
  layoutPhase: "ready" as const,
  navigateToNode: () => undefined,
  setHoverEq: () => undefined,
  setSelected: () => undefined,
};

const ATTACK_SET = String.raw`$$
\mathbb{D}_{\text{attack}} \;=\; \big\{\, \big((n(x), y),\; s_i\big) \;:\; |Y_{\text{match}}(x)| = 1,\; i \in Y_{\text{match}}(x) \,\big\}
$$`;

describe("RichMarkdown", () => {
  it("preserves inline math delimiters through CommonMark parsing", () => {
    const markup = renderToStaticMarkup(
      <RichMarkdown glossary={{}} markdown={String.raw`Scale by \(\sqrt{d_k}\).`} />,
    );

    expect(markup).toContain(String.raw`\(\sqrt{d_k}\)`);
  });

  it("renders the reported display equation without CommonMark corruption", () => {
    const markup = renderToStaticMarkup(
      <RichMarkdown glossary={{}} markdown={ATTACK_SET} />,
    );

    expect(markup).toContain("katex-display");
    expect(markup).toContain(String.raw`\mathbb{D}_{\text{attack}}`);
    expect(markup).not.toContain(";=;");
  });
});

describe("Drawer", () => {
  it("renders the selected concept explanation from the deterministic fixture", () => {
    const markup = renderToStaticMarkup(
      <DrawerPresentation
        {...drawerActions}
        selected="scaled-dot-product-attention"
      />,
    );

    expect(markup).toContain("Scaled Dot-Product Attention");
    expect(markup).toContain("The Math");
    expect(markup).toContain("eq_1");
    expect(markup).toContain(String.raw`\sqrt{d_k}`);
    expect(markup).toContain("Query vectors used to request relevant information.");
    expect(markup).toContain(
      "concept · sec:3.2.1 · unlocks 2 concept(s) directly, 2 more downstream",
    );
  });

  it("orders plain-words lead before equations, with meta demoted to the end", () => {
    const markup = renderToStaticMarkup(
      <DrawerPresentation {...drawerActions} selected="scaled-dot-product-attention" />,
    );
    const lead = markup.indexOf("drawer-lead");
    const eq = markup.indexOf("drawer-equations");
    const meta = markup.indexOf("drawer-meta");
    expect(lead).toBeGreaterThanOrEqual(0);
    expect(lead).toBeLessThan(eq);
    expect(eq).toBeLessThan(meta);
  });

  it("renders TL;DR as an always-open lead, not a collapsible summary", () => {
    const markup = renderToStaticMarkup(
      <DrawerPresentation {...drawerActions} selected="scaled-dot-product-attention" />,
    );
    expect(markup).toContain("drawer-lead");
    expect(markup).not.toContain("<summary>TL;DR</summary>");
  });

  it("keeps Intuition open and The Math collapsed", () => {
    const markup = renderToStaticMarkup(
      <DrawerPresentation {...drawerActions} selected="scaled-dot-product-attention" />,
    );
    const chunks = markup.split("<details");
    const intuition = chunks.find((chunk) => chunk.includes("<summary>Intuition</summary>"));
    const theMath = chunks.find((chunk) => chunk.includes("<summary>The Math</summary>"));
    expect(intuition).toMatch(/^ open/);
    expect(theMath).toBeDefined();
    expect(theMath).not.toMatch(/^ open/);
  });

  it("does not render a code disclosure for a concept node with no code or bridge", () => {
    const markup = renderToStaticMarkup(
      <DrawerPresentation {...drawerActions} selected="scaled-dot-product-attention" />,
    );
    expect(markup).not.toContain("See it in code");
  });

  it("renders no transient content for an invalid selection", () => {
    const markup = renderToStaticMarkup(
      <DrawerPresentation {...drawerActions} selected="missing-node" />,
    );

    expect(markup).toBe("");
  });

  it("keeps equation highlighting active while either pointer or focus remains", () => {
    expect(equationHoverValue("eq_1", true, false)).toBe("eq_1");
    expect(equationHoverValue("eq_1", false, true)).toBe("eq_1");
    expect(equationHoverValue("eq_1", true, true)).toBe("eq_1");
    expect(equationHoverValue("eq_1", false, false)).toBeNull();
  });

  it("restores the focused equation after a different hovered pill leaves", () => {
    type EquationState = {
      focused: string | null;
      hovered: string | null;
    };
    type EquationEvent = {
      type: "focus" | "blur" | "enter" | "leave";
      equation: string;
    };
    let state: EquationState = { focused: null, hovered: null };
    state = nextEquationInteraction(state, { type: "focus", equation: "eq_A" });
    expect(activeEquation(state)).toBe("eq_A");
    state = nextEquationInteraction(state, { type: "enter", equation: "eq_B" });
    expect(activeEquation(state)).toBe("eq_B");
    state = nextEquationInteraction(state, { type: "leave", equation: "eq_B" });
    expect(activeEquation(state)).toBe("eq_A");
    state = nextEquationInteraction(state, { type: "blur", equation: "eq_A" });
    expect(activeEquation(state)).toBeNull();
  });

  it("associates a disabled bridge with its ready-state reason", () => {
    const markup = renderToStaticMarkup(
      <BridgeButton
        id="attention-code"
        label="Compute attention"
        layoutPhase="loading"
        navigateToNode={() => undefined}
        relation="implemented by"
        targetExists
      />,
    );

    expect(markup).toContain("disabled");
    expect(markup).toMatch(/aria-describedby="[^"]+"/);
    expect(markup).toContain("Graph layout is still loading.");
  });
});
