import katex from "katex";
import {
  Children,
  cloneElement,
  Fragment,
  isValidElement,
  useEffect,
  useId,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import ReactMarkdown from "react-markdown";
import rehypeKatex from "rehype-katex";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";

import { KE_DATA } from "../data.gen";
import { parseContent } from "../lib/contentBlocks";
import { dependencyRings } from "../lib/deps";
import { pageMarkdownFor } from "../lib/learnPath";
import {
  safeKatexOptions,
  safeKatexPluginOptions,
  restoreEscapedDollars,
  splitTiers,
  preserveMathForMarkdown,
  tokenizeRichText,
  type RichTextToken,
} from "../lib/mathHtml";
import { navigationDisabledReason } from "../lib/navigation";
import { getViz } from "../lib/viz";
import { useApp, type LayoutPhase } from "../store";
import type { KEEdge, KENode } from "../types";
import BlockRenderer from "./blocks/BlockRenderer";
import CodeViewer, { hasCodeFor } from "./CodeViewer";
import { useNodeNavigation } from "./useNodeNavigation";
import VizTier from "./VizTier";

type DrawerNode = KENode & { page?: string; anchor?: string };
type Note = { synthesis?: string; status?: string; date?: string };

const NODES = KE_DATA.nodes as DrawerNode[];
const EDGES = KE_DATA.edges as KEEdge[];
const PAGES = KE_DATA.pages as Record<string, string>;
const NOTES = KE_DATA.notes as Record<string, Note>;
const GLOSSARY = KE_DATA.glossary as Record<string, Record<string, string>>;
const EQ_INDEX = KE_DATA.eqIndex as Record<string, string[]>;

export type Bridge = { id: string; relation: "implemented by" | "implements" };

/** The "See it in code" links for `selected`: which code nodes implement it,
 *  and which it implements. Pure over `edges` so it is testable with an
 *  injected bridge (the shipped AIAYN fixture carries no `implements` edges). */
export function deriveBridges(
  selected: string | null,
  edges: KEEdge[],
): Bridge[] {
  if (!selected) return [];
  const relationships: Bridge[] = [];
  edges.forEach((edge) => {
    if (edge.kind !== "implements") return;
    if (edge.dst === selected) {
      relationships.push({ id: edge.src, relation: "implemented by" });
    } else if (edge.src === selected) {
      relationships.push({ id: edge.dst, relation: "implements" });
    }
  });
  return relationships;
}

const TIER_ORDER = [
  "tldr",
  "intuition",
  "mechanics",
  "the-math",
  "go-deeper",
] as const;

const DEEPER_TIERS = ["intuition", "mechanics", "the-math", "go-deeper"] as const;

const TIER_LABEL: Record<(typeof TIER_ORDER)[number], string> = {
  tldr: "TL;DR",
  intuition: "Intuition",
  mechanics: "Mechanics",
  "the-math": "The Math",
  "go-deeper": "Go Deeper",
};

function GlossaryTerm({ definition, value }: { definition: string; value: string }) {
  const tooltipId = useId();
  return (
    <span
      aria-describedby={tooltipId}
      className="tooltip"
      tabIndex={0}
    >
      {value}
      <span className="tooltip-content" id={tooltipId} role="tooltip">
        {definition}
      </span>
    </span>
  );
}

function MathFragment({ token }: { token: Extract<RichTextToken, { kind: "math" }> }) {
  let html: string | null = null;
  try {
    html = katex.renderToString(token.tex, safeKatexOptions(token.display));
  } catch {
    // Invalid TeX remains visible as inert text.
  }

  return html ? (
    <span
      aria-label={token.source}
      className={token.display ? "math math-display" : "math"}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  ) : (
    <span
      aria-label={token.source}
      className={token.display ? "math math-display" : "math"}
    >{token.source}</span>
  );
}

function RichText({ glossary, text }: {
  glossary: Record<string, string>;
  text: string;
}) {
  return tokenizeRichText(text, glossary).map((token, index) => {
    const key = `${token.kind}-${index}`;
    if (token.kind === "text") return token.value;
    if (token.kind === "glossary") {
      return <GlossaryTerm {...token} key={key} />;
    }
    return <MathFragment key={key} token={token} />;
  });
}

type MarkdownAstNode = {
  type?: string;
  value?: string;
  children?: MarkdownAstNode[];
};

function rehypeRestoreEscapedDollars() {
  return (tree: MarkdownAstNode) => {
    const visit = (node: MarkdownAstNode) => {
      if (node.type === "text" && typeof node.value === "string") {
        node.value = restoreEscapedDollars(node.value);
      }
      node.children?.forEach(visit);
    };
    visit(tree);
  };
}

function hasKatexClass(child: ReactNode) {
  if (!isValidElement<{ className?: unknown }>(child)) return false;
  const className = child.props.className;
  return typeof className === "string"
    && className.split(/\s+/).some((name) => (
      name === "katex" || name === "katex-display" || name === "katex-error"
    ));
}

function decorateChildren(
  children: ReactNode,
  glossary: Record<string, string>,
): ReactNode {
  return Children.map(children, (child) => {
    if (typeof child === "string") {
      return <RichText glossary={glossary} text={child} />;
    }
    if (
      isValidElement<{ children?: ReactNode }>(child)
      && child.props.children !== undefined
      && child.type !== "code"
      && !hasKatexClass(child)
    ) {
      return cloneElement(
        child,
        undefined,
        decorateChildren(child.props.children, glossary),
      );
    }
    return child;
  });
}

/** Markdown that may contain typed content-block fences (annotated-eq,
 *  derivation, algorithm, figure) — segments render through BlockRenderer so
 *  the drawer shows the same rich blocks as the article. */
export function BlockContent({ glossary, markdown }: {
  glossary: Record<string, string>;
  markdown: string;
}) {
  const segments = useMemo(() => parseContent(markdown), [markdown]);
  return (
    <>
      {segments.map((segment, index) => (
        <BlockRenderer
          key={`${segment.type}-${index}`}
          renderMarkdown={(md) => <RichMarkdown glossary={glossary} markdown={md} />}
          segment={segment}
        />
      ))}
    </>
  );
}

export function RichMarkdown({ glossary, markdown }: {
  glossary: Record<string, string>;
  markdown: string;
}) {
  const components = useMemo(() => ({
    p: ({ node: _node, children, ...props }: React.ComponentPropsWithoutRef<"p"> & { node?: unknown }) => (
      <p {...props}>{decorateChildren(children, glossary)}</p>
    ),
    li: ({ node: _node, children, ...props }: React.ComponentPropsWithoutRef<"li"> & { node?: unknown }) => (
      <li {...props}>{decorateChildren(children, glossary)}</li>
    ),
    td: ({ node: _node, children, ...props }: React.ComponentPropsWithoutRef<"td"> & { node?: unknown }) => (
      <td {...props}>{decorateChildren(children, glossary)}</td>
    ),
    th: ({ node: _node, children, ...props }: React.ComponentPropsWithoutRef<"th"> & { node?: unknown }) => (
      <th {...props}>{decorateChildren(children, glossary)}</th>
    ),
  }), [glossary]);

  return (
    <ReactMarkdown
      components={components}
      rehypePlugins={[
        [rehypeKatex, safeKatexPluginOptions()],
        rehypeRestoreEscapedDollars,
      ]}
      remarkPlugins={[
        remarkGfm,
        [remarkMath, { singleDollarTextMath: true }],
      ]}
    >
      {preserveMathForMarkdown(markdown)}
    </ReactMarkdown>
  );
}

export function equationHoverValue(
  equation: string,
  hovered: boolean,
  focused: boolean,
) {
  return activeEquation({
    focused: focused ? equation : null,
    hovered: hovered ? equation : null,
  });
}

export type EquationInteractionState = {
  focused: string | null;
  hovered: string | null;
};

export type EquationInteractionEvent = {
  type: "focus" | "blur" | "enter" | "leave";
  equation: string;
};

export function activeEquation(state: EquationInteractionState) {
  return state.hovered ?? state.focused;
}

export function nextEquationInteraction(
  state: EquationInteractionState,
  event: EquationInteractionEvent,
): EquationInteractionState {
  if (event.type === "focus") return { ...state, focused: event.equation };
  if (event.type === "enter") return { ...state, hovered: event.equation };
  if (event.type === "blur") {
    return state.focused === event.equation
      ? { ...state, focused: null }
      : state;
  }
  return state.hovered === event.equation
    ? { ...state, hovered: null }
    : state;
}

function EquationButton({
  equation,
  onInteraction,
}: {
  equation: string;
  onInteraction: (event: EquationInteractionEvent) => void;
}) {
  return (
    <button
      aria-label={`Highlight nodes linked to ${equation}`}
      className="drawer-equation"
      onBlur={() => onInteraction({ type: "blur", equation })}
      onFocus={() => onInteraction({ type: "focus", equation })}
      onMouseEnter={() => onInteraction({ type: "enter", equation })}
      onMouseLeave={() => onInteraction({ type: "leave", equation })}
      type="button"
    >
      {equation}
    </button>
  );
}

function EquationList({
  equations,
  setHoverEq,
}: {
  equations: string[];
  setHoverEq: (equation: string | null) => void;
}) {
  const [interaction, setInteraction] = useState<EquationInteractionState>({
    focused: null,
    hovered: null,
  });
  const highlighted = activeEquation(interaction);

  useEffect(() => setHoverEq(highlighted), [highlighted, setHoverEq]);
  useEffect(() => () => setHoverEq(null), [setHoverEq]);

  return (
    <div className="drawer-equation-list">
      {equations.map((equation) => (
        <EquationButton
          equation={equation}
          key={equation}
          onInteraction={(event) => {
            setInteraction((current) => nextEquationInteraction(current, event));
          }}
        />
      ))}
    </div>
  );
}

export function BridgeButton({
  id,
  label,
  layoutPhase,
  navigateToNode,
  relation,
  targetExists,
}: {
  id: string;
  label: string;
  layoutPhase: LayoutPhase;
  navigateToNode: (nodeId: string) => void;
  relation: "implemented by" | "implements";
  targetExists: boolean;
}) {
  const reasonId = useId();
  const disabledReason = navigationDisabledReason(layoutPhase, targetExists);

  return (
    <>
      <button
        aria-describedby={disabledReason ? reasonId : undefined}
        className="drawer-bridge"
        disabled={disabledReason !== null}
        onClick={() => navigateToNode(id)}
        title={disabledReason ?? undefined}
        type="button"
      >
        <span>{relation}</span>
        <strong>{label}</strong>
      </button>
      {disabledReason && (
        <span className="sr-only" id={reasonId}>{disabledReason}</span>
      )}
    </>
  );
}

export type DrawerPresentationProps = {
  selected: string | null;
  layoutPhase: LayoutPhase;
  onClose?: () => void;
  setSelected: (selected: string | null) => void;
  setHoverEq: (equation: string | null) => void;
  navigateToNode: (nodeId: string) => void;
};

export function DrawerPresentation({
  selected,
  layoutPhase,
  onClose,
  setSelected,
  setHoverEq,
  navigateToNode,
}: DrawerPresentationProps) {
  const node = useMemo(
    () => NODES.find((candidate) => candidate.id === selected),
    [selected],
  );
  const pageMarkdown = node ? pageMarkdownFor(node, PAGES) : undefined;
  const note = selected ? NOTES[selected] : undefined;
  const glossary = selected ? GLOSSARY[selected] ?? {} : {};
  const tiers = useMemo(
    () => splitTiers(pageMarkdown ?? ""),
    [pageMarkdown],
  );
  const rings = useMemo(
    () => selected ? dependencyRings(selected, EDGES) : new Map<string, number>(),
    [selected],
  );
  const equations = useMemo(
    () => selected
      ? Object.entries(EQ_INDEX)
        .filter(([, nodeIds]) => nodeIds.includes(selected))
        .map(([equation]) => equation)
      : [],
    [selected],
  );
  const bridges = useMemo<Bridge[]>(
    () => deriveBridges(selected, EDGES),
    [selected],
  );

  if (!selected) return null;
  if (!node) return null;

  const immediateImpact = [...rings.values()].filter((depth) => depth === 1).length;
  const secondaryImpact = [...rings.values()].filter((depth) => depth === 2).length;
  const hasDeeperTiers = DEEPER_TIERS.some((tier) => tiers[tier]);
  const fallbackMarkdown = note?.synthesis?.trim();
  const hasCode = hasCodeFor(selected);
  const viz = getViz(selected);

  return (
    <div className="drawer-content">
      <div className="drawer-heading">
        <div>
          <p className="drawer-eyebrow">Explain</p>
          <h2 className="drawer-title" tabIndex={-1}>{node.label}</h2>
        </div>
        <button
          aria-label="Close explanation"
          className="drawer-close"
          onClick={() => closeDrawer({ onClose, setSelected })}
          type="button"
        >
          Close
        </button>
      </div>

      {tiers.tldr && (
        <section aria-label="In plain words" className="drawer-lead">
          <RichMarkdown glossary={glossary} markdown={tiers.tldr} />
        </section>
      )}

      {pageMarkdown && hasDeeperTiers && (
        <section aria-label="Explanation tiers" className="tier">
          {!tiers.intuition && viz && <VizTier entry={viz} nodeId={selected} />}
          {DEEPER_TIERS.filter((tier) => tiers[tier]).map((tier) => (
            <Fragment key={tier}>
              <details open={tier === "intuition"}>
                <summary>{TIER_LABEL[tier]}</summary>
                <div className="tier-body">
                  <BlockContent glossary={glossary} markdown={tiers[tier] ?? ""} />
                </div>
              </details>
              {tier === "intuition" && viz && (
                <VizTier entry={viz} nodeId={selected} />
              )}
            </Fragment>
          ))}
        </section>
      )}

      {viz && !(pageMarkdown && hasDeeperTiers) && (
        <section aria-label="Explanation tiers" className="tier">
          <VizTier entry={viz} nodeId={selected} />
        </section>
      )}

      {!tiers.tldr && !hasDeeperTiers && (
        fallbackMarkdown ? (
          <section aria-label="Research note" className="drawer-note">
            <h3>Research note</h3>
            <RichMarkdown glossary={glossary} markdown={fallbackMarkdown} />
          </section>
        ) : pageMarkdown ? (
          <section aria-label="Explanation" className="drawer-note">
            <RichMarkdown glossary={glossary} markdown={pageMarkdown} />
          </section>
        ) : (
          <p className="drawer-empty">no page or note for this node yet</p>
        )
      )}

      {equations.length > 0 && (
        <section aria-labelledby="drawer-equations-heading" className="drawer-section drawer-equations">
          <h3 id="drawer-equations-heading">Key equations — hover to highlight in the graph</h3>
          <EquationList
            equations={equations}
            key={selected}
            setHoverEq={setHoverEq}
          />
        </section>
      )}

      {(bridges.length > 0 || hasCode) && (
        <details className="drawer-section drawer-code">
          <summary>See it in code</summary>
          {bridges.length > 0 && (
            <div className="drawer-bridge-list">
              {bridges.map(({ id, relation }) => {
                const target = NODES.find((candidate) => candidate.id === id);
                return (
                  <BridgeButton
                    id={id}
                    key={`${relation}-${id}`}
                    label={target?.label ?? id}
                    layoutPhase={layoutPhase}
                    navigateToNode={navigateToNode}
                    relation={relation}
                    targetExists={Boolean(target)}
                  />
                );
              })}
            </div>
          )}
          <CodeViewer embedded nodeId={selected} />
        </details>
      )}

      <p className="drawer-meta">
        {node.kind} · {node.source_ref ?? "—"} · unlocks {immediateImpact} concept(s) directly, {secondaryImpact} more downstream
      </p>
    </div>
  );
}

export function closeDrawer({
  onClose,
  setSelected,
}: {
  onClose?: () => void;
  setSelected: (selected: string | null) => void;
}) {
  if (onClose) onClose();
  else setSelected(null);
}

export default function Drawer({ onClose }: { onClose?: () => void }) {
  const selected = useApp((state) => state.selected);
  const setSelected = useApp((state) => state.setSelected);
  const setHoverEq = useApp((state) => state.setHoverEq);
  const layoutPhase = useApp((state) => state.layoutPhase);
  const navigateToNode = useNodeNavigation();

  return (
    <DrawerPresentation
      layoutPhase={layoutPhase}
      navigateToNode={navigateToNode}
      onClose={onClose}
      selected={selected}
      setHoverEq={setHoverEq}
      setSelected={setSelected}
    />
  );
}
