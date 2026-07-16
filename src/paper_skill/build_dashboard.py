"""End-to-end paper -> concept graph, with the anti-TOC guard wired in.

This is the canonical build path. Every LLM stage takes an injectable
``spawn`` (default: the ``claude`` CLI via :mod:`llm_spawn`, which fails loudly
when absent). Concept extraction is passed through :func:`concepts.require_ok`,
so a paper whose extraction fails aborts the build instead of silently shipping
a table-of-contents dashboard -- the historical failure mode.

Page writing (p4_write) pulls in optional deps (research_mcp); it is imported
lazily so graph-only builds work without them.
"""
import json
from pathlib import Path

from .concepts import extract_concepts, is_toc_graph, require_ok
from .llm_spawn import claude_spawn
from .paper2pack import build_pack


def build_graph(target: str, spawn=claude_spawn, *, cache_dir=None) -> dict:
    """Build a *validated* concept graph for ``target`` (arXiv id / .tex / .pdf).

    Raises ``ConceptExtractionError`` rather than degrading to section headings.
    """
    pack = build_pack(target, cache_dir=cache_dir)
    if pack.get("status"):
        raise RuntimeError(f"paper2pack failed for {target!r}: {pack}")
    result = require_ok(extract_concepts(pack, spawn))
    graph = result["graph"]
    if is_toc_graph(graph):  # defensive tripwire: a validated graph should not look like a TOC
        raise RuntimeError(
            f"extraction returned a table-of-contents-shaped graph for {target!r}"
        )
    return {"pack": pack, "graph": graph, "toc": result["toc"]}


def write_graph(target: str, out_dir: str, spawn=claude_spawn) -> Path:
    """Build and persist ``<out_dir>/{pack,concept-graph}.json``; return out_dir."""
    built = build_graph(target, spawn)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "pack.json").write_text(
        json.dumps(built["pack"], ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "concept-graph.json").write_text(
        json.dumps({"toc": built["toc"], **built["graph"]},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    return out
