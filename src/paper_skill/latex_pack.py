"""Rung-1 pack builder: pylatexenc walk (never regex over TeX, round-6)."""
import datetime
import re
from pylatexenc.latexwalker import (LatexWalker, LatexEnvironmentNode,
                                    LatexMacroNode, LatexCharsNode,
                                    LatexGroupNode)

_SECTION_MACROS = {"section": 1, "subsection": 2, "subsubsection": 3}
_EQ_ENVS = {"equation", "equation*", "align", "align*", "eqnarray", "displaymath"}


def _flatten_inputs(tex: str, resolve_input, depth=0) -> str:
    if resolve_input is None or depth > 5:
        return tex
    def sub(m):
        return _flatten_inputs(resolve_input(m.group(1)) or "", resolve_input, depth + 1)
    return re.sub(r"\\input\{([^}]+)\}", sub, tex)


def _strip_comments(tex: str) -> str:
    return re.sub(r"(?<!\\)%.*", "", tex)


def _group_text(node) -> str:
    if isinstance(node, LatexGroupNode):
        return "".join(_group_text(n) for n in node.nodelist)
    if isinstance(node, LatexCharsNode):
        return node.chars
    if isinstance(node, LatexMacroNode):
        # Recurse into the argument so \emph{Causal} contributes "Causal"
        # instead of vanishing. Bare macros (\\, \thanks) have no args and
        # collapse to "", which _clean then folds into surrounding space.
        return " ".join(_group_text(a) for a in (node.nodeargd.argnlist
                                                 if node.nodeargd else []) if a)
    return ""


def _clean(text: str) -> str:
    return " ".join(text.split())


def _find_title(nodelist) -> str:
    """First \\title{...} anywhere in the document, including inside groups."""
    for n in nodelist or []:
        if isinstance(n, LatexMacroNode) and n.macroname == "title":
            if n.nodeargd and n.nodeargd.argnlist:
                return _clean(_group_text(n.nodeargd.argnlist[-1]))
        if isinstance(n, (LatexEnvironmentNode, LatexGroupNode)):
            found = _find_title(n.nodelist)
            if found:
                return found
    return ""


_MACRO_DEF = re.compile(
    r"\\(newcommand|renewcommand|providecommand|DeclareMathOperator)(\*?)\s*"
    r"(?:\{\\([A-Za-z@]+)\}|\\([A-Za-z@]+))\s*(?:\[\d+\])?\s*(?:\[[^\]]*\])?\s*\{")


def _read_group(tex: str, open_brace: int) -> tuple[str, int]:
    """Return the balanced-brace body starting at ``open_brace`` and its end.

    Macro bodies nest ({\\mathcal{#1}}), so brace counting is required -- a
    non-greedy regex stops at the first } and truncates the definition.
    """
    depth, i = 0, open_brace
    while i < len(tex):
        if tex[i] == "\\":
            i += 2
            continue
        if tex[i] == "{":
            depth += 1
        elif tex[i] == "}":
            depth -= 1
            if depth == 0:
                return tex[open_brace + 1:i], i + 1
        i += 1
    return "", len(tex)


def _optional_arg_macros(tex: str) -> set:
    """Names declared like ``\\newcommand{\\pa}[2][]{...}`` — optional first arg."""
    return {m.group(1) or m.group(2) for m in re.finditer(
        r"\\(?:new|renew|provide)command\s*(?:\{\\([A-Za-z@]+)\}|\\([A-Za-z@]+))"
        r"\s*\[\d+\]\s*\[", tex)}


def normalize_optional_args(latex: str, names: set) -> str:
    """Rewrite ``\\pa[\\G]X`` as ``\\pa{\\G}X`` for optional-arg macros.

    KaTeX has no optional-argument macros -- feeding it the declaration throws
    -- so the call sites are converted to the brace form its #1/#2 substitution
    already understands. Scoped to macros actually declared that way, because a
    bracket after any other command is ordinary content such as an interval.
    """
    for name in names:
        latex = re.sub(r"\\" + re.escape(name) + r"\[([^\[\]]*)\]",
                       lambda m: "\\" + name + "{" + m.group(1) + "}", latex)
    return latex


def extract_macros(tex: str) -> dict:
    """Preamble macro definitions as a KaTeX ``macros`` table.

    Equations are copied VERBATIM from the source (equation_fidelity "exact"),
    so a paper's own notation travels with them. Without the definitions KaTeX
    throws on the first unknown command and the reader is shown raw LaTeX --
    \\doo instead of "do". KaTeX uses the same #1 placeholders as LaTeX, so
    bodies pass through untouched; only \\DeclareMathOperator needs rewriting,
    since KaTeX has no such primitive.
    """
    macros: dict[str, str] = {}
    for m in _MACRO_DEF.finditer(tex):
        kind, star, name = m.group(1), m.group(2), m.group(3) or m.group(4)
        body, _ = _read_group(tex, m.end() - 1)
        if not name:
            continue
        if kind == "DeclareMathOperator":
            body = f"\\operatorname{star}{{{body}}}"
        # A macro body carries the same bookkeeping an equation body does, and
        # a numbering-only macro (\eqnr and friends) reduces to nothing --
        # which is correct: it never contributed maths, only a counter.
        macros["\\" + name] = _EMPTY_TAG.sub("", _BOOKKEEPING.sub("", body)).strip()
    return macros


# Bookkeeping that carries no maths: cross-reference anchors, the numbering
# suppressors, and LaTeX's counter machinery. KaTeX implements none of it, and
# one occurrence anywhere in a body loses the WHOLE equation to the raw-LaTeX
# fallback -- so this is stripped from equations and from macro bodies alike.
_BOOKKEEPING = re.compile(
    r"\\(?:label\s*\{[^{}]*\}"
    r"|(?:add|set|ref|step)?(?:to)?counter\s*(?:\{[^{}]*\}){1,2}"
    r"|the[a-zA-Z]+\b|nonumber\b|notag\b)")
# \tag{} left behind once its \thecounter argument is gone renders an empty tag.
_EMPTY_TAG = re.compile(r"\\tag\*?\s*\{\s*\}")


def _needs_alignment(latex: str) -> bool:
    """True when an ``&`` or ``\\\\`` sits outside every environment.

    Such a body came from an align/eqnarray wrapper this extractor drops, so
    the markers are left with nothing to align against. Testing for the mere
    PRESENCE of an environment is not enough: a body can open an array, close
    it, and only then use a top-level ``&``.
    """
    depth = i = 0
    while i < len(latex):
        if latex[i] == "\\":
            for token, step in ((r"\begin{", 7), (r"\end{", 5), ("\\\\", 2)):
                if latex.startswith(token, i):
                    if token == r"\begin{":
                        depth += 1
                    elif token == r"\end{":
                        depth -= 1
                    elif depth == 0:
                        return True
                    i += step
                    break
            else:
                i += 2          # any other escape, \& and \% included
            continue
        if latex[i] == "&" and depth == 0:
            return True
        i += 1
    return False


def normalize_math(latex: str) -> str:
    """Make an extracted equation body renderable without changing its maths.

    Three rules, each about LaTeX in general rather than any one paper:
    strip bookkeeping; collapse the blank lines _strip_comments leaves where
    ``%`` lines were (illegal inside LaTeX math, and they end the markdown
    paragraph, tearing the ``$$`` block in half); and give orphaned alignment
    markers the ``aligned`` environment they need. Idempotent, because a body
    that already has its own environment is left alone.
    """
    latex = _EMPTY_TAG.sub("", _BOOKKEEPING.sub("", latex))
    latex = re.sub(r"\n\s*\n+", "\n", latex).strip()
    if _needs_alignment(latex):
        latex = "\\begin{aligned}\n" + latex + "\n\\end{aligned}"
    return latex


def latex_to_pack(main_tex: str, resolve_input=None, source: str = "",
                  title: str = "") -> dict:
    tex = _strip_comments(_flatten_inputs(main_tex, resolve_input))
    optional_args = _optional_arg_macros(tex)
    nodes, _, _ = LatexWalker(tex).get_latex_nodes()
    sections, equations = [], []
    counters = [0, 0, 0]
    cur_id, buf = None, []

    def flush():
        if cur_id is not None and sections:
            sections[-1]["text"] = " ".join("".join(buf).split())
        buf.clear()

    def walk(nodelist):
        nonlocal cur_id
        for n in nodelist or []:
            if isinstance(n, LatexMacroNode) and n.macroname in _SECTION_MACROS:
                flush()
                lvl = _SECTION_MACROS[n.macroname]
                counters[lvl - 1] += 1
                for i in range(lvl, 3):
                    counters[i] = 0
                cur_id = "sec_" + "_".join(str(c) for c in counters[:lvl])
                stitle = ""
                if n.nodeargd and n.nodeargd.argnlist:
                    stitle = _clean(_group_text(n.nodeargd.argnlist[-1]))
                sections.append({"id": cur_id, "title": stitle,
                                 "level": lvl, "text": ""})
            elif isinstance(n, LatexEnvironmentNode) and n.environmentname in _EQ_ENVS:
                latex = tex[n.nodelist[0].pos:n.nodelist[-1].pos
                            + n.nodelist[-1].len] if n.nodelist else ""
                equations.append({"id": f"eq_{len(equations) + 1}",
                                  "latex": normalize_math(normalize_optional_args(
                                      latex.strip(), optional_args)),
                                  "section": cur_id or "sec_0"})
            elif isinstance(n, LatexCharsNode):
                buf.append(n.chars)
            elif isinstance(n, (LatexEnvironmentNode, LatexGroupNode)):
                walk(n.nodelist)

    walk(nodes)
    flush()
    return {"meta": {"source": source, "title": title or _find_title(nodes),
                     "generated": datetime.date.today().isoformat()},
            "extraction": {"path": "latex", "equation_fidelity": "exact"},
            "sections": sections, "equations": equations,
            "macros": extract_macros(tex),
            "references": [], "figures": []}
