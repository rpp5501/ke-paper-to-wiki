import json
from pathlib import Path

from paper_skill.build_dashboard import build_graph

OUT = Path(__file__).resolve().parent
PDF = r"C:\Users\Rp\OneDrive\Desktop\Fall 2025\EE456\2205.06900v2 (2).pdf"


def main():
    authored = json.loads((OUT / "concept-graph.json").read_text(encoding="utf-8"))
    response = json.dumps({"nodes": authored["nodes"], "edges": authored["edges"]})

    def luna_spawn(prompt: str) -> str:
        return response

    built = build_graph(PDF, spawn=luna_spawn)
    graph = built["graph"]
    graph["meta"]["model"] = "gpt-5.6-luna"
    (OUT / "concept-graph.json").write_text(
        json.dumps({"toc": built["toc"], **graph}, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    (OUT / "toc.json").write_text(
        json.dumps({"model": "gpt-5.6-luna", "source": built["pack"]["meta"]["source"], "rows": built["toc"]}, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    (OUT / "canonical-graph-report.json").write_text(
        json.dumps({"model": "gpt-5.6-luna", "status": "ok", "nodes": len(graph["nodes"]), "edges": len(graph["edges"]), "root_count": sum(n.get("level") == 0 for n in graph["nodes"])}, indent=1),
        encoding="utf-8",
    )
    print(json.dumps({"status": "ok", "nodes": len(graph["nodes"]), "edges": len(graph["edges"]), "root_count": sum(n.get("level") == 0 for n in graph["nodes"])}, indent=1))


if __name__ == "__main__":
    main()
