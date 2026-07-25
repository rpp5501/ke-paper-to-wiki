"""R15.10 — concept_graph.json → Mermaid mindmap (shareable spatial overview).

Mermaid's mindmap syntax is strictly a tree, so only the `part-of` hierarchy
(src = part, dst = whole) becomes the map. Every non-tree edge (prerequisite,
builds-on, ...) is preserved as a footer comment — nothing is silently lost.

Usage: python -m paper_skill.graph_to_mermaid <concept_graph.json> [--out map.mmd]
GitHub and Obsidian render the output natively inside ```mermaid fences.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

INDENT = "  "


def _sanitize(label: str) -> str:
    """Mermaid mindmap labels break on parens/brackets; keep it plain."""
    return "".join(c for c in label if c not in "()[]{}").strip() or "untitled"


def to_mermaid_mindmap(graph: dict, max_depth: int = 0) -> str:
    """max_depth mirrors the dashboard's R16.B1 branch collapse: 0 means the
    whole tree, N keeps depths 1..N and reports the count it folded away."""
    nodes = {n["id"]: n for n in graph.get("nodes", [])}
    children: dict[str, list[str]] = {}
    parented: set[str] = set()
    for e in graph.get("edges", []):
        if e.get("kind") == "part-of" and e["src"] in nodes and e["dst"] in nodes:
            children.setdefault(e["dst"], []).append(e["src"])
            parented.add(e["src"])

    roots = sorted(
        (n for n in nodes.values() if n["id"] not in parented),
        key=lambda n: (int(n.get("level", 9)), n["id"]),
    )
    if not roots:
        raise ValueError("no root: every node has a part-of parent (cycle?)")
    root, orphans = roots[0], roots[1:]

    lines = ["mindmap"]
    shown: set[str] = set()

    def emit(node_id: str, depth: int, seen: frozenset[str]) -> None:
        if node_id in seen:  # defensive: part-of cycles must not hang us
            return
        if max_depth and depth > max_depth:
            return
        label = _sanitize(nodes[node_id].get("label", node_id))
        shape = f"(({label}))" if depth == 1 else label
        lines.append(INDENT * depth + shape)
        shown.add(node_id)
        for child in sorted(children.get(node_id, [])):
            emit(child, depth + 1, seen | {node_id})

    emit(root["id"], 1, frozenset())
    for orphan in orphans:  # unparented non-roots stay visible under the root
        emit(orphan["id"], 2, frozenset())

    hidden = len(nodes) - len(shown)
    if max_depth and hidden:  # nothing silently lost, same as the edge footer
        lines.append("")
        lines.append(f"%% {hidden} node(s) hidden below depth {max_depth}")

    non_tree = [e for e in graph.get("edges", []) if e.get("kind") != "part-of"]
    if non_tree:
        lines.append("")
        lines.append("%% non-tree edges (mindmap syntax cannot draw these):")
        for e in non_tree:
            lines.append(f"%% {e['src']} --{e['kind']}--> {e['dst']}")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="paper_skill.graph_to_mermaid")
    p.add_argument("graph")
    p.add_argument("--out", help="output .mmd path (default: stdout)")
    p.add_argument("--max-depth", type=int, default=0,
                   help="keep only depths 1..N of the part-of tree "
                        "(default: the whole tree)")
    a = p.parse_args(argv)
    text = to_mermaid_mindmap(
        json.loads(Path(a.graph).read_text(encoding="utf-8")),
        max_depth=a.max_depth)
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
        print(f"{a.out}: {len(text.splitlines())} lines")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
