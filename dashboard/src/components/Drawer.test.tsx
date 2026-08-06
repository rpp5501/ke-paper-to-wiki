import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import * as DrawerModule from "./Drawer";

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
  it("renders standard single-dollar inline math in the reported sentence", () => {
    const markdown = String.raw`The detection input is the model itself: $g_c(\cdot)$ is queried over the input domain $\mathcal{X}$, while the clean sample set $D$ appears only in the mitigation problem [§sec_1].`;
    const markup = renderToStaticMarkup(
      <RichMarkdown glossary={{}} markdown={markdown} />,
    );

    expect(markup.match(/class="katex"/g)).toHaveLength(3);
    expect(markup).not.toContain("$g_c");
    expect(markup).not.toContain("$\\mathcal{X}$");
    expect(markup).toContain("§sec_1");
  });

  it("keeps legacy inline math rendering through the standard pipeline", () => {
    const markup = renderToStaticMarkup(
      <RichMarkdown glossary={{}} markdown={String.raw`Scale by \(\sqrt{d_k}\).`} />,
    );

    expect(markup).toContain('class="katex"');
    expect(markup).not.toContain(String.raw`\(\sqrt{d_k}\)`);
  });

  it("renders math in lists and GFM tables", () => {
    const markdown = String.raw`- score $g_c(x)$

| domain |
| --- |
| $\mathcal{X}$ |`;
    const markup = renderToStaticMarkup(
      <RichMarkdown glossary={{}} markdown={markdown} />,
    );

    expect(markup).toContain("<li>");
    expect(markup).toContain("<table>");
    expect(markup.match(/class="katex"/g)).toHaveLength(2);
  });

  it("preserves code and escaped currency as prose", () => {
    const markdown = "Cost is \\$5; keep `$g_c(x)$` literal.\n\n"
      + "```tex\n"
      + "$D$\n"
      + "```";
    const markup = renderToStaticMarkup(
      <RichMarkdown glossary={{}} markdown={markdown} />,
    );

    expect(markup).toContain("Cost is $5");
    expect(markup).toContain("<code>$g_c(x)$</code>");
    expect(markup).toContain("<code class=\"language-tex\">$D$");
  });

  it("requires literal currency to be escaped while later math renders", () => {
    const markup = renderToStaticMarkup(
      <RichMarkdown glossary={{}} markdown={"Costs \\$5; let $x$ vary"} />,
    );

    expect(markup).toContain("Costs $5; let ");
    expect(markup.match(/class="katex"/g)).toHaveLength(1);
    expect(markup).not.toContain("$x$");
  });

  it("restores escaped prose dollars in headings", () => {
    const markup = renderToStaticMarkup(
      <RichMarkdown glossary={{}} markdown={String.raw`# Cost \$5`} />,
    );

    expect(markup).toContain("<h1>Cost $5</h1>");
    expect(markup).not.toContain("\uE000");
  });

  it("keeps escaped-dollar TeX inside standard inline math", () => {
    const markdown = String.raw`$2\$x$`;
    const markup = renderToStaticMarkup(
      <RichMarkdown glossary={{}} markdown={markdown} />,
    );

    expect(markup.match(/class="katex"/g)).toHaveLength(1);
    expect(markup).not.toContain("\uE000");
    expect(markup).not.toContain(markdown);
  });

  it("renders TeX ending in an escaped dollar without merging delimiters", () => {
    const markdown = String.raw`$2\$$`;
    const markup = renderToStaticMarkup(
      <RichMarkdown glossary={{}} markdown={markdown} />,
    );

    expect(markup.match(/class="katex"/g)).toHaveLength(1);
    expect(markup).not.toContain("\uE000");
    expect(markup).not.toContain("\uE001");
    expect(markup).not.toContain(markdown);
  });

  it("recognizes an inline-math closer after an even backslash run", () => {
    const markdown = String.raw`$x\\$ price \$5 and $z$`;
    const markup = renderToStaticMarkup(
      <RichMarkdown glossary={{}} markdown={markdown} />,
    );

    expect(markup.match(/class="katex"/g)).toHaveLength(2);
    expect(markup).toContain("price $5 and ");
    expect(markup).not.toContain("\uE000");
    expect(markup).not.toContain("\uE001");
  });

  it("recognizes an inline-math opener after an even backslash run", () => {
    const markdown = String.raw`\\$x$`;
    const markup = renderToStaticMarkup(
      <RichMarkdown glossary={{}} markdown={markdown} />,
    );

    expect(markup.match(/class="katex"/g)).toHaveLength(1);
    expect(markup).not.toContain("\uE000");
  });

  it("keeps an inline-math opener after an odd backslash run as prose", () => {
    const markdown = String.raw`\$x$`;
    const markup = renderToStaticMarkup(
      <RichMarkdown glossary={{}} markdown={markdown} />,
    );

    expect(markup).not.toContain('class="katex"');
    expect(markup).toContain("$x$");
    expect(markup).not.toContain("\uE000");
  });

  it.each([
    "$2x$",
    "$2 + 2$",
    "$0.5$",
    "$2x^2$",
    String.raw`$2\pi$`,
    "$2(x+1)$",
    String.raw`$2\cdot x$`,
  ])("renders numeric-leading standard math case %#", (markdown) => {
    const markup = renderToStaticMarkup(
      <RichMarkdown glossary={{}} markdown={markdown} />,
    );

    expect(markup).toContain('class="katex"');
    expect(markup).not.toContain(markdown);
  });

  it("keeps glossary decoration outside KaTeX output", () => {
    const markup = renderToStaticMarkup(
      <RichMarkdown
        glossary={{ model: "A learned function." }}
        markdown={String.raw`model $\operatorname{model}(x)$`}
      />,
    );

    expect(markup.match(/class="tooltip"/g)).toHaveLength(1);
    expect(markup).toContain('class="katex"');
  });

  it("leaves malformed TeX visible without throwing", () => {
    const markup = renderToStaticMarkup(
      <RichMarkdown glossary={{}} markdown={String.raw`Before $\notACommand{$ after.`} />,
    );

    expect(markup).toContain("Before");
    expect(markup).toContain("after");
    expect(markup).toContain("katex-error");
  });

  it("renders the reported display equation without CommonMark corruption", () => {
    const markup = renderToStaticMarkup(
      <RichMarkdown glossary={{}} markdown={ATTACK_SET} />,
    );

    expect(markup).toContain("katex-display");
    expect(markup).toContain("mathbb");
    expect(markup).toContain("attack");
    expect(markup).not.toContain(";=;");
  });
});

describe("Drawer", () => {
  it("uses the panel close callback without clearing graph selection", () => {
    const closeDrawer = (DrawerModule as unknown as {
      closeDrawer?: (actions: {
        onClose?: () => void;
        setSelected: (selected: string | null) => void;
      }) => void;
    }).closeDrawer;
    expect(typeof closeDrawer).toBe("function");
    if (!closeDrawer) return;
    let closed = false;
    let cleared = false;

    closeDrawer({
      onClose: () => { closed = true; },
      setSelected: () => { cleared = true; },
    });

    expect(closed).toBe(true);
    expect(cleared).toBe(false);
  });

  it("renders the selected concept explanation from the deterministic fixture", () => {
    const markup = renderToStaticMarkup(
      <DrawerPresentation
        {...drawerActions}
        selected="structural-intervention-distance"
      />,
    );

    expect(markup).toContain("Structural Intervention Distance (SID)");
    expect(markup).toContain("The Math");
    expect(markup).toContain("eq_4");
    expect(markup).toContain("intervention");
    expect(markup).toContain("drawer-meta");
  });

  it("orders plain-words lead before equations, with meta demoted to the end", () => {
    const markup = renderToStaticMarkup(
      <DrawerPresentation {...drawerActions} selected="structural-intervention-distance" />,
    );
    const lead = markup.indexOf("drawer-lead");
    const eq = markup.indexOf("<summary>The Math</summary>");
    const meta = markup.indexOf("drawer-meta");
    expect(lead).toBeGreaterThanOrEqual(0);
    expect(lead).toBeLessThan(eq);
    expect(eq).toBeLessThan(meta);
  });

  it("renders TL;DR as an always-open lead, not a collapsible summary", () => {
    const markup = renderToStaticMarkup(
      <DrawerPresentation {...drawerActions} selected="structural-intervention-distance" />,
    );
    expect(markup).toContain("drawer-lead");
    expect(markup).not.toContain("<summary>TL;DR</summary>");
  });

  it("keeps Intuition open and The Math collapsed", () => {
    const markup = renderToStaticMarkup(
      <DrawerPresentation {...drawerActions} selected="structural-intervention-distance" />,
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
      <DrawerPresentation {...drawerActions} selected="graph-comparison-problem" />,
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
