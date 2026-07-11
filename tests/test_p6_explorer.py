import json
from pathlib import Path

from paper_skill.p6_explorer import build_explorer, split_tiers


PAGE = """# SDPA
## TL;DR {#tldr}
Short.
## Intuition {#intuition}
Feel.
## Mechanics {#mechanics}
Divide [eq_1].
## The Math {#the-math}
$$\\sqrt{d_k}$$
## Go Deeper {#go-deeper}
- link
"""


def test_split_tiers_five_keys():
    tiers = split_tiers(PAGE)
    assert set(tiers) == {"tldr", "intuition", "mechanics", "the-math", "go-deeper"}
    assert "Short." in tiers["tldr"]


def test_math_becomes_math_span():
    tiers = split_tiers(PAGE)
    assert '<span class="math">' in tiers["the-math"]
    assert "\\sqrt{d_k}" in tiers["the-math"]


def test_build_explorer_end_to_end(tmp_path):
    graph = json.loads(
        (Path(__file__).resolve().parents[1] / "fixtures" / "aiayn_concept_graph.json").read_text(
            encoding="utf-8"
        )
    )
    pages = tmp_path / "pages"
    pages.mkdir()
    (pages / "01_scaled-dot-product-attention.md").write_text(PAGE, encoding="utf-8")
    pack = {
        "meta": {"source": "arXiv:1706.03762", "title": "AIAYN", "generated": "x"},
        "extraction": {},
        "sections": [],
        "equations": [],
        "references": [],
        "figures": [],
    }
    out = tmp_path / "explorer.html"

    result = build_explorer(pack, graph, pages, out)

    assert result["status"] == "ok"
    html = out.read_text(encoding="utf-8")
    assert "\\sqrt{d_k}" in html and "KaTeX" in html
    assert "unpkg.com" not in html
