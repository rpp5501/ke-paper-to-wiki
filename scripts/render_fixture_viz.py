"""M4 render harness: AIAYN §5.1 fixture → graphify viz HTML.

Usage (from Deepwiki root, graphify fork on PYTHONPATH):
    PYTHONPATH="Forked repos/graphify" python paper-skill/scripts/render_fixture_viz.py

Offline note: graphify's viz loads vis-network from unpkg. To view with no
network, vendor it once next to the output HTML:
    curl -o paper-skill/fixtures/vis-network.min.js \
        https://unpkg.com/vis-network@9.1.6/standalone/umd/vis-network.min.js
then replace the unpkg <script src> in the HTML with "vis-network.min.js"
(fork strip pass will make this the default).
"""
import json
import sys
from pathlib import Path

import networkx as nx

from graphify.exporters.html import to_html
from graphify.schema_adapter import to_graphify

HERE = Path(__file__).resolve().parent
FIXTURE = HERE.parent / "fixtures" / "aiayn_concept_graph.json"
OUT = HERE.parent / "fixtures" / "aiayn_viz.html"


def main() -> int:
    plan_graph = json.loads(FIXTURE.read_text(encoding="utf-8"))
    g = to_graphify(plan_graph)

    G = nx.Graph()
    for n in g["nodes"]:
        G.add_node(n["id"], **{k: v for k, v in n.items() if k != "id"})
    for e in g["edges"]:
        G.add_edge(e["source"], e["target"],
                   **{k: v for k, v in e.items() if k not in ("source", "target")})

    # single community until Leiden lands (M3)
    to_html(G, {0: list(G.nodes)}, str(OUT),
            community_labels={0: plan_graph["meta"].get("source", "concept graph")})

    html = OUT.read_text(encoding="utf-8")
    labels_ok = all(
        (n["label"] in html) or (json.dumps(n["label"])[1:-1] in html)
        for n in g["nodes"]
    )
    print(f"wrote {OUT} ({len(html)} bytes)")
    print(f"nodes: {G.number_of_nodes()} | edges: {G.number_of_edges()} | all labels present: {labels_ok}")
    return 0 if labels_ok else 1


if __name__ == "__main__":
    sys.exit(main())
