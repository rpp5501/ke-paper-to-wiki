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
    assert "$$\\sqrt{d_k}$$" in tiers["the-math"]


def test_math_is_sanitized_without_markdown_mangling():
    page = PAGE.replace(
        "$$\\sqrt{d_k}$$",
        r"$$\label{eq:test}\maximize_x a_b & = c \\ d$$",
    )

    math = split_tiers(page)["the-math"]

    assert r"\label" not in math
    assert r"\operatorname*{maximize}" in math
    assert r"\begin{aligned}" in math
    assert "<em>" not in math


def test_bare_resource_url_is_clickable_and_keeps_punctuation():
    page = PAGE.replace("- link", "See https://example.test/guide.")

    deeper = split_tiers(page)["go-deeper"]

    assert '<a href="https://example.test/guide">https://example.test/guide</a>.' in deeper


def test_build_explorer_end_to_end(tmp_path):
    graph = json.loads(
        (Path(__file__).resolve().parents[1] / "fixtures" / "aiayn_concept_graph.json").read_text(
            encoding="utf-8"
        )
    )
    matching_node = next(
        node for node in graph["nodes"] if node["id"] == "scaled-dot-product-attention"
    )
    matching_node.pop("page")
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
    assert r"$$\\sqrt{d_k}$$" in html
    assert "unpkg.com" not in html
    assert matching_node["page"] == "01_scaled-dot-product-attention.md"
    assert matching_node["anchor"] == "#mechanics"


def test_build_explorer_preserves_existing_page_metadata(tmp_path):
    graph = {
        "nodes": [
            {
                "id": "scaled-dot-product-attention",
                "label": "SDPA",
                "page": "existing-page.md",
            }
        ],
        "edges": [],
    }
    pages = tmp_path / "pages"
    pages.mkdir()
    (pages / "01_scaled-dot-product-attention.md").write_text(PAGE, encoding="utf-8")
    pack = {"meta": {"title": "AIAYN"}}

    build_explorer(pack, graph, pages, tmp_path / "explorer.html")

    assert graph["nodes"][0]["page"] == "existing-page.md"
    assert graph["nodes"][0]["anchor"] == "#tldr"
