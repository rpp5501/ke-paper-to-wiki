"""Lint rules for rich content blocks and paragraph length.

lint_page splits Mechanics/The Math on blank lines to find unanchored claims.
A fenced YAML content block contains blank lines, so left alone it is torn in
half and its anchor-less first fragment reported as an unanchored claim -- the
identical failure already fixed for $$...$$ display math.
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


# Once P4 gets repo_dir, pages cite the implementation as well as the paper --
# 27 such references across the 24 SID pages. The anchor rule exists so a claim
# is traceable, and a claim about the code is traceable by pointing at the
# code; without this, 16 of 26 "unanchored claims" were paragraphs that carried
# a perfectly good reference of the wrong shape.
def test_a_code_reference_anchors_a_claim():
    assert _lint("The loop squares the matrix [sid.py:L24].") == []


def test_a_bare_filename_reference_anchors_too():
    assert _lint("Handled by the helper [sid.py].") == []


def test_a_claim_with_no_reference_of_any_kind_is_still_caught():
    assert any("unanchored" in p
               for p in _lint("The loop squares the matrix repeatedly."))


def test_prose_mentioning_a_module_is_not_an_anchor():
    """Only a bracketed reference counts; naming a file mid-sentence does not."""
    assert any("unanchored" in p
               for p in _lint("The code in sid.py squares the matrix twice."))


def test_formatting_is_not_linted():
    """Length, bullets and tables are PAGE_PROMPT's business, not the linter's.

    A ceiling was tried and removed: every lint problem is blocking (see
    scripts/gate_slice7.py), so a style preference became a build failure and
    took the judgement away from the writer that can see the content.
    """
    wall = " ".join(["word"] * 200) + " [§sec_3]"
    assert _lint(wall) == []


def test_a_page_with_no_table_and_no_list_still_passes():
    assert _lint("Short and anchored [§sec_3].") == []
