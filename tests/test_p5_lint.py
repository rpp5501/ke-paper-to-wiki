from paper_skill.p5_lint import lint_page

PACK = {"sections": [{"id": "sec_3", "title": "S", "level": 1, "text": "t"}],
        "equations": [{"id": "eq_1", "latex": "x", "section": "sec_3"}],
        "meta": {}, "extraction": {}, "references": [], "figures": []}

CLEAN = """# C
## TL;DR {#tldr}
Fine.
## Intuition {#intuition}
Fine.
## Mechanics {#mechanics}
Divided by sqrt(d_k) [eq_1].
## The Math {#the-math}
Variance grows [§sec_3].
## Go Deeper {#go-deeper}
- [d2l](https://d2l.ai/x)
"""


def test_clean_page_lints_empty():
    assert lint_page(CLEAN, PACK, check_links=lambda url: True) == []


def test_dangling_anchor_caught():
    bad = CLEAN.replace("[eq_1]", "[eq_9]")
    probs = lint_page(bad, PACK, check_links=lambda url: True)
    assert any("eq_9" in p for p in probs)


def test_unanchored_math_claim_caught():
    bad = CLEAN.replace("Variance grows [§sec_3].", "Variance grows a lot.")
    probs = lint_page(bad, PACK, check_links=lambda url: True)
    assert any("unanchored" in p for p in probs)


def test_dead_link_caught():
    probs = lint_page(CLEAN, PACK, check_links=lambda url: False)
    assert any("dead link" in p for p in probs)
