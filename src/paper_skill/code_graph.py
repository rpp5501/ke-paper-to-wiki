"""A §5.1 code graph for any path — the code half of the M6 bridge.

research-mcp/scripts/dogfood_graph.py could only graph research-mcp: its ROOT
came from the script's own location. Bridging a paper to whatever implements it
needs that extraction pointed anywhere, so it lives here as an importable
function with the graphify call injected, the way the LLM stages inject spawn.

Extraction is keyless: graphify's AST path needs no model for code corpora.

Usage: python -m paper_skill.code_graph <path> [-o code-graph.json] [--source X]
"""
import json
import subprocess
import sys
from pathlib import Path

_GRAPHIFY_PKG = Path(__file__).resolve().parents[3] / "Forked repos" / "graphify"


def _to_plan_schema(native: dict, source: str) -> dict:
    if str(_GRAPHIFY_PKG) not in sys.path:
        sys.path.insert(0, str(_GRAPHIFY_PKG))
    from graphify.schema_adapter import to_plan_schema_native
    return to_plan_schema_native(native, source=source)


def run_graphify(target: Path) -> dict:
    """Extract ``target`` (a directory) and return graphify's native graph.

    ``graphify <path>`` writes graphify-out/ *under* the resolved target, so
    this runs `graphify .` with cwd=target to keep the output next to the code
    being graphed rather than wherever the caller happens to stand.
    """
    binary = Path(sys.executable).parent / (
        "graphify.exe" if sys.platform == "win32" else "graphify")
    subprocess.run([str(binary) if binary.exists() else "graphify",
                    ".", "--code-only"], cwd=target, check=True)
    out = Path(target) / "graphify-out" / "graph.json"
    if not out.is_file():
        raise RuntimeError(f"graphify wrote no graph at {out}")
    return json.loads(out.read_text(encoding="utf-8"))


def _source_file(node: dict) -> str:
    return str(node.get("source_ref", "")).split(":L", 1)[0].replace("\\", "/")


def build_code_graph(target, source: str | None = None, run=run_graphify) -> dict:
    """Build a §5.1 code graph for ``target`` (a file or a directory)."""
    target = Path(target)
    scan_dir = target.parent if target.is_file() else target
    native = run(scan_dir)
    # networkx node_link_data calls them "links"; §5.1 calls them "edges".
    # Getting this wrong is silent -- the adapter simply sees none and returns
    # an edgeless graph, which reads downstream as "this code has no structure".
    native = {**native, "edges": native.get("edges") or native.get("links") or []}

    # graphify tags docstrings and explanatory comments file_type "rationale".
    # The §5.1 kind enum has no such value, so the adapter's .get(..., "function")
    # default would type a module's prose as callables -- 4 of the 10 nodes in
    # pgmpy's sid.py. Dropped here, keyed on graphify's own type rather than a
    # guess at the label's shape.
    prose = {n["id"] for n in native["nodes"]
             if n.get("file_type") == "rationale"}
    if prose:
        native = {**native,
                  "nodes": [n for n in native["nodes"] if n["id"] not in prose],
                  "edges": [e for e in native["edges"]
                            if e["source"] not in prose and e["target"] not in prose]}

    graph = _to_plan_schema(native, source or f"repo:{Path(target).name}")

    if target.is_file():
        # graphify only walks directories, so narrowing to one module happens
        # after extraction rather than by pointing the extractor at the file.
        keep = {n["id"] for n in graph["nodes"]
                if _source_file(n).endswith(target.name)}
        graph["nodes"] = [n for n in graph["nodes"] if n["id"] in keep]
        graph["edges"] = [e for e in graph["edges"]
                          if e["src"] in keep and e["dst"] in keep]

    if not graph["nodes"]:
        # §5.1 requires minItems 1. Failing loudly beats shipping an empty
        # graph that reads as "no structure here" instead of "nothing ran".
        raise RuntimeError(
            f"no code nodes extracted from {target} -- refusing to emit an "
            "empty code graph. Check that graphify is installed "
            '(pip install -e "Forked repos/graphify") and the path has source '
            "files in a language it parses.")
    return graph


def main(argv=None, run=run_graphify) -> int:
    import argparse
    p = argparse.ArgumentParser(prog="paper_skill.code_graph")
    p.add_argument("target", help="file or directory to extract")
    p.add_argument("-o", "--output", default="code-graph.json")
    p.add_argument("--source", help="meta.source label (default: repo:<name>)")
    a = p.parse_args(argv)

    graph = build_code_graph(a.target, source=a.source, run=run)
    Path(a.output).write_text(
        json.dumps(graph, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{a.output}: {len(graph['nodes'])} nodes, {len(graph['edges'])} edges")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
