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
    return ""


def latex_to_pack(main_tex: str, resolve_input=None, source: str = "",
                  title: str = "") -> dict:
    tex = _strip_comments(_flatten_inputs(main_tex, resolve_input))
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
                    stitle = _group_text(n.nodeargd.argnlist[-1]).strip()
                sections.append({"id": cur_id, "title": stitle,
                                 "level": lvl, "text": ""})
            elif isinstance(n, LatexEnvironmentNode) and n.environmentname in _EQ_ENVS:
                latex = tex[n.nodelist[0].pos:n.nodelist[-1].pos
                            + n.nodelist[-1].len] if n.nodelist else ""
                equations.append({"id": f"eq_{len(equations) + 1}",
                                  "latex": latex.strip(),
                                  "section": cur_id or "sec_0"})
            elif isinstance(n, LatexCharsNode):
                buf.append(n.chars)
            elif isinstance(n, (LatexEnvironmentNode, LatexGroupNode)):
                walk(n.nodelist)

    walk(nodes)
    flush()
    return {"meta": {"source": source, "title": title,
                     "generated": datetime.date.today().isoformat()},
            "extraction": {"path": "latex", "equation_fidelity": "exact"},
            "sections": sections, "equations": equations,
            "references": [], "figures": []}
