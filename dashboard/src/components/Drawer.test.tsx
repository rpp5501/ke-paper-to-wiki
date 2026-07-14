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

describe("RichMarkdown", () => {
  it("preserves inline math delimiters through CommonMark parsing", () => {
    const markup = renderToStaticMarkup(
      <RichMarkdown glossary={{}} markdown={String.raw`Scale by \(\sqrt{d_k}\).`} />,
    );

    expect(markup).toContain(String.raw`\(\sqrt{d_k}\)`);
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
      "concept · sec:3.2.1 · depends-on-this: immediate 2, secondary 2",
    );
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
