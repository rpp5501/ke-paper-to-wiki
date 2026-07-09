"""Inline the fixture graph into the explorer template so explorer.html works over file://."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def build(fixture="fixtures/aiayn_concept_graph.json",
          template="explorer/template.html",
          out="explorer/explorer.html"):
    graph = json.dumps(json.loads((ROOT / fixture).read_text(encoding="utf-8")))
    html = (ROOT / template).read_text(encoding="utf-8")
    if "/*GRAPH_JSON*/" not in html:
        raise SystemExit("template missing /*GRAPH_JSON*/ placeholder")
    (ROOT / out).write_text(html.replace("/*GRAPH_JSON*/", graph), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    build()
