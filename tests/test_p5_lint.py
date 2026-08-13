import pytest

from paper_skill.p5_lint import lint_page, _mermaid_ok

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


# PAGE_PROMPT requires equations be reproduced VERBATIM from the pack, and real
# paper LaTeX contains blank lines inside align/array blocks. Splitting
# paragraphs on blank lines therefore tore a $$...$$ block in half and reported
# the anchor-less first half as an unanchored claim. Seen on arXiv:1306.1043.
BLANK_LINE_IN_MATH = """# C
## TL;DR {#tldr}
Fine.
## Intuition {#intuition}
Fine.
## Mechanics {#mechanics}
Divided by sqrt(d_k) [eq_1].
## The Math {#the-math}
The definition is stated as [eq_1]:

$$
\\begin{array}{rcl}
\\mathrm{SID} &\\rightarrow& \\mathbb{N}

(\\G,\\HH) &\\mapsto& \\#\\{(i,j)\\}
\\end{array}
$$ [eq_1]

## Go Deeper {#go-deeper}
- [d2l](https://d2l.ai/x)
"""


# p4_write's PAGE_PROMPT forbids tiers whose content is that they have no
# content. A prompt rule is a hope; this is the check. Real examples from
# arXiv:1306.1043 before the rule existed:
#   "No equations were supplied in the local context for this concept ..."
#   "The local context describes complexity in prose rather than as a ..."
@pytest.mark.parametrize("filler", [
    "No equations were supplied in the local context for this concept [§sec_3].",
    "The local context does not include a labeled equation here [§sec_3].",
    "No [eq_N]-tagged equations are present for this concept [§sec_3].",
    "No formal expression can be reproduced here without fabricating it [§sec_3].",
])
def test_a_tier_that_only_reports_its_own_emptiness_is_caught(filler):
    page = CLEAN.replace("Variance grows [§sec_3].", filler)

    probs = lint_page(page, PACK, check_links=lambda url: True)

    assert any("no-content" in p for p in probs), probs


def test_real_material_mentioning_equations_is_not_flagged():
    """The rule targets tiers ABOUT their own emptiness, not any sentence that
    happens to say "equation" — that would ban ordinary maths writing."""
    page = CLEAN.replace(
        "Variance grows [§sec_3].",
        "The equation is derived by expanding the quadratic form [eq_1].")

    assert lint_page(page, PACK, check_links=lambda url: True) == []


def test_blank_line_inside_display_math_is_not_an_unanchored_claim():
    probs = lint_page(BLANK_LINE_IN_MATH, PACK, check_links=lambda url: True)
    assert probs == []


def test_a_genuinely_unanchored_equation_is_still_caught():
    """Folding display math must not become a blanket exemption for it."""
    bad = BLANK_LINE_IN_MATH.replace("$$ [eq_1]", "$$")
    probs = lint_page(bad, PACK, check_links=lambda url: True)
    assert any("unanchored" in p for p in probs)


WITH_MERMAID = CLEAN.replace(
    "- [d2l](https://d2l.ai/x)",
    "- [d2l](https://d2l.ai/x)\n```mermaid\ngraph TD; A-->B;\n```",
)


def test_skipped_mermaid_check_does_not_fail_an_otherwise_clean_page():
    # check_mermaid=None (skipped) must never be treated as a problem —
    # "skipped, not pass" per the plan's own offline-lint constraint.
    probs = lint_page(WITH_MERMAID, PACK, check_links=lambda url: True,
                      check_mermaid=lambda block: None)
    assert probs == []


def test_mermaid_parse_failure_is_still_caught():
    probs = lint_page(WITH_MERMAID, PACK, check_links=lambda url: True,
                      check_mermaid=lambda block: False)
    assert any("fails to parse" in p for p in probs)


def test_mermaid_ok_treats_missing_package_as_skipped_not_failed(monkeypatch):
    # Exit code 2 = mermaid_parse.mjs's own "module not found" signal —
    # must be treated as skipped (None), not a parse failure (False).
    class FakeCompleted:
        returncode = 2

    import subprocess as sp
    monkeypatch.setattr(sp, "run", lambda *a, **kw: FakeCompleted())
    assert _mermaid_ok("graph TD; A-->B;") is None


def test_no_content_filler_catches_the_relevance_phrasing():
    """The contract names "no display equation is relevant here" as a checked
    failure, so the check has to actually catch it -- otherwise the rule is
    advice the writer can ignore without consequence. The zero-equation
    chain-of-thought pages reached for this exact wording."""
    from paper_skill.p5_lint import lint_page

    pack = {"sections": [{"id": "sec_1", "title": "T", "text": "x"}],
            "equations": [], "figures": [], "references": []}
    page = ("# X\n## TL;DR {#tldr}\na\n## Intuition {#intuition}\nb\n"
            "## Mechanics {#mechanics}\nc [§sec_1]\n"
            "## The Math {#the-math}\n"
            "No display equation is relevant for this concept [§sec_1].\n"
            "## Go Deeper {#go-deeper}\n- x\n")

    problems = lint_page(page, pack, check_links=lambda _u: True,
                         check_mermaid=lambda _b: None)

    assert any("no-content filler" in p for p in problems), problems


_TAB_FIG_PACK = {
    "sections": [{"id": "sec_1", "title": "T", "text": "x"}],
    "equations": [],
    "tables": [{"id": "tab_1", "section": "sec_1", "caption": "c", "rows": [["a"]]}],
    "figures": [{"id": "fig_1", "section": "sec_1", "caption": "c"}],
    "references": [],
}


def _lint(page):
    from paper_skill.p5_lint import lint_page
    return lint_page(page, _TAB_FIG_PACK, check_links=lambda _u: True,
                     check_mermaid=lambda _b: None)


def test_a_table_citation_counts_as_an_anchor():
    """p4_context offers the writer [tab_N] as evidence and the contract asks
    results pages to reproduce the paper's numbers, but _ANCHOR only ever
    matched sections, equations and [S1]. So a paragraph citing a table read as
    an unanchored claim. Harmless while lint only wrote a report; blocking the
    moment the write gate started running it, and it accounted for most of the
    DDIM regeneration failures."""
    page = ("# X\n## TL;DR {#tldr}\na\n## Intuition {#intuition}\nb\n"
            "## Mechanics {#mechanics}\nc [§sec_1]\n"
            "## The Math {#the-math}\n"
            "Doubling S cuts the error from 0.0140 to 0.0065 [tab_1].\n"
            "## Go Deeper {#go-deeper}\n- x\n")

    assert not [p for p in _lint(page) if "unanchored" in p]


def test_a_figure_citation_counts_as_an_anchor():
    page = ("# X\n## TL;DR {#tldr}\na\n## Intuition {#intuition}\nb\n"
            "## Mechanics {#mechanics}\n"
            "The experiment shown uses fifty steps [fig_1].\n"
            "## The Math {#the-math}\nSee the table [§sec_1].\n"
            "## Go Deeper {#go-deeper}\n- x\n")

    assert not [p for p in _lint(page) if "unanchored" in p]


def test_an_invented_table_id_is_still_caught():
    """Accepting the namespace must not mean accepting any id in it."""
    page = ("# X\n## TL;DR {#tldr}\na\n## Intuition {#intuition}\nb\n"
            "## Mechanics {#mechanics}\nc [§sec_1]\n"
            "## The Math {#the-math}\nNumbers come from nowhere [tab_99].\n"
            "## Go Deeper {#go-deeper}\n- x\n")

    assert any("dangling anchor: tab_99" in p for p in _lint(page))


def test_a_pack_with_no_tables_or_figures_still_lints():
    """packs predating table/figure extraction have no such keys at all."""
    from paper_skill.p5_lint import lint_page

    old = {"sections": [{"id": "sec_1", "title": "T", "text": "x"}],
           "equations": [], "references": []}
    page = ("# X\n## TL;DR {#tldr}\na\n## Intuition {#intuition}\nb\n"
            "## Mechanics {#mechanics}\nc [§sec_1]\n"
            "## The Math {#the-math}\nd [§sec_1]\n"
            "## Go Deeper {#go-deeper}\n- x\n")

    assert lint_page(page, old, check_links=lambda _u: True,
                     check_mermaid=lambda _b: None) == []


def test_a_colon_lead_in_is_carried_by_the_block_it_introduces():
    """"The identity-shortcut form of the block is:" followed by an anchored
    display equation is not an unanchored claim -- the lead-in and the block
    are one thought, and the evidence sits on the block. Splitting on blank
    lines tore them apart, which was the single largest cause of failure in the
    resnet run (25 of 53 recorded problems) and hit every "here are the
    numbers:" lead-in before a table too.
    """
    from paper_skill.p5_lint import lint_page

    pack = {"sections": [{"id": "sec_1", "title": "T", "text": "x"}],
            "equations": [{"id": "eq_1", "latex": "y", "section": "sec_1"}],
            "references": []}
    page = ("# X\n## TL;DR {#tldr}\na\n## Intuition {#intuition}\nb\n"
            "## Mechanics {#mechanics}\nc [§sec_1]\n"
            "## The Math {#the-math}\n"
            "The identity-shortcut form of the block is:\n\n"
            "$$y = F(x) + x$$ [eq_1]\n"
            "## Go Deeper {#go-deeper}\n- x\n")

    assert not [p for p in lint_page(page, pack, check_links=lambda _u: True,
                                     check_mermaid=lambda _b: None)
                if "unanchored" in p]


def test_a_lead_in_to_an_unanchored_block_is_still_caught():
    """Merging must not become a way to launder a claim that cites nothing."""
    from paper_skill.p5_lint import lint_page

    pack = {"sections": [{"id": "sec_1", "title": "T", "text": "x"}],
            "equations": [], "references": []}
    page = ("# X\n## TL;DR {#tldr}\na\n## Intuition {#intuition}\nb\n"
            "## Mechanics {#mechanics}\nc [§sec_1]\n"
            "## The Math {#the-math}\n"
            "The three cases the proof considers are:\n\n"
            "Something asserted with no evidence at all here.\n"
            "## Go Deeper {#go-deeper}\n- x\n")

    assert [p for p in lint_page(page, pack, check_links=lambda _u: True,
                                 check_mermaid=lambda _b: None)
            if "unanchored" in p]
