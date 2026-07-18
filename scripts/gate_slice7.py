# scripts/gate_slice7.py
"""Slice-7 paper acceptance (§4.3), deterministic half — paper-agnostic. Usage:
PYTHONPATH="src:../research-mcp/src" python scripts/gate_slice7.py pack.json concept_graph.json pages/"""
import json, re, sys
from pathlib import Path
from paper_skill.p5_lint import lint_page

pack = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
graph = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
pages = sorted(Path(sys.argv[3]).glob("*.md"))
texts = [p.read_text(encoding="utf-8") for p in pages]

# A page carries a renderable equation when it holds a display ($$..$$) or inline
# (\(..\)) math block. Gate only applies when the source actually has equations,
# so equation-free sources (e.g. degraded PDF-rung packs) pass honestly.
_MATH = re.compile(r"\$\$.+?\$\$|\\\(.+?\\\)", re.S)
has_equations = bool(pack.get("equations"))

n = len(graph["nodes"])
checks = {
    "15-25 concept nodes": 15 <= n <= 25,
    "one page per included concept": len(pages) >= n - 2,
    "all pages lint clean": all(not lint_page(t, pack) for t in texts),
    "math tier carries the source's equations": (not has_equations)
                                                 or any(_MATH.search(t) for t in texts),
}
for name, ok in checks.items():
    print(("PASS " if ok else "FAIL "), name)
sys.exit(0 if all(checks.values()) else 1)
