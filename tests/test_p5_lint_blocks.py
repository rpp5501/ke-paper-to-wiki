"""Lint rules for rich content blocks and paragraph length.

lint_page splits Mechanics/The Math on blank lines to find unanchored claims.
A fenced YAML content block contains blank lines, so left alone it is torn in
half and its anchor-less first fragment reported as an unanchored claim -- the
identical failure already fixed for $$...$$ display math.

The paragraph ceiling is the only formatting check. "Should have used a table"
is a judgement a linter cannot make; "this is a 101-word wall" is arithmetic.
"""
from paper_skill.p5_lint import lint_page

PACK = {"sections": [{"id": "sec_3", "title": "S", "level": 1, "text": "t"}],
        "equations": [{"id": "eq_1", "latex": "x", "section": "sec_3"}],
        "meta": {}, "extraction": {}, "references": [], "figures": []}

BLOCK = """```algorithm
title: Reachability

lines:
  - code: "for _ in range(k):"

    intent: "Each squaring doubles the path length covered [§sec_3]"
```"""


def _page(math_body):
    return ("# C\n## TL;DR {#tldr}\nFine.\n## Intuition {#intuition}\nFine.\n"
            "## Mechanics {#mechanics}\nAnchored [eq_1].\n"
            f"## The Math {{#the-math}}\n{math_body}\n"
            "## Go Deeper {#go-deeper}\n- none\n")


def _lint(body):
    return lint_page(_page(body), PACK, check_links=lambda url: True,
                     check_mermaid=lambda block: None)


def test_a_content_block_survives_the_paragraph_split():
    assert _lint(BLOCK) == []


def test_a_block_with_no_anchor_anywhere_is_still_caught():
    """The fold is not an amnesty."""
    assert any("unanchored" in p
               for p in _lint(BLOCK.replace(" [§sec_3]", "")))


def test_a_long_prose_paragraph_is_flagged():
    wall = " ".join(["word"] * 100) + " [§sec_3]"
    assert any("long paragraph" in p for p in _lint(wall))


def test_a_paragraph_under_the_ceiling_is_not_flagged():
    assert _lint(" ".join(["word"] * 80) + " [§sec_3]") == []


def test_a_long_display_equation_is_not_flagged():
    """LaTeX array bodies word-count high; they are not walls of text."""
    body = "$$\n" + " \\\\ ".join(["a_{i} &= b_{i}"] * 40) + "\n$$ [eq_1]"
    assert not any("long paragraph" in p for p in _lint(body))


def test_a_long_content_block_is_not_flagged():
    lines = "\n".join(
        [f'  - code: "step {i}"\n    intent: "does a thing [§sec_3]"'
         for i in range(30)])
    assert not any("long paragraph" in p
                   for p in _lint("```algorithm\nlines:\n" + lines + "\n```"))


def test_a_page_with_no_table_and_no_list_still_passes():
    """Absence of structure is not a defect -- a quota would produce tables
    comparing one thing."""
    assert _lint("Short and anchored [§sec_3].") == []
