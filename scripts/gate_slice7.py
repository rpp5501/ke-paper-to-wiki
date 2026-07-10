# scripts/gate_slice7.py
"""AIAYN acceptance (§4.3), deterministic half. Usage:
PYTHONPATH="src:../research-mcp/src" python scripts/gate_slice7.py pack.json concept_graph.json pages/"""
import json, sys
from pathlib import Path
from paper_skill.p5_lint import lint_page

pack = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
graph = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
pages = sorted(Path(sys.argv[3]).glob("*.md"))

n = len(graph["nodes"])
checks = {
    "15-25 concept nodes": 15 <= n <= 25,
    "one page per included concept": len(pages) >= n - 2,
    "all pages lint clean": all(not lint_page(p.read_text(encoding='utf-8'), pack)
                                for p in pages),
    "sqrt(d_k) math tier exists": any("sqrt{d_k}" in p.read_text(encoding="utf-8")
                                      or "√" in p.read_text(encoding="utf-8")
                                      for p in pages),
}
for name, ok in checks.items():
    print(("PASS " if ok else "FAIL "), name)
sys.exit(0 if all(checks.values()) else 1)
