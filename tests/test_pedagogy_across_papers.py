"""The pedagogy gates have to work on papers that are not about causal DAGs.

The first version of the diagram check was built while looking at one paper and
scored every page of the Transformer build zero -- including the encoder-decoder
stack, the page in that whole build most in need of a picture -- while flagging
six pages of the backdoor-attack paper because "backdoor" there means a planted
trojan, not a back-door path. These tests hold the gates to behaving per paper.
"""
from pathlib import Path

import pytest

from paper_skill.pedagogy import (
    DIAGRAM_SIGNAL_FLOOR,
    figure_count,
    is_results_page,
    pedagogy_problems,
    structural_signals,
)

ARTIFACTS = Path(__file__).resolve().parents[1] / "artifacts"


def _pages(name):
    directory = ARTIFACTS / name / "pages"
    if not directory.is_dir():
        pytest.skip(f"{name} artifact not present")
    return {p.stem.split("_", 1)[-1]: p.read_text(encoding="utf-8")
            for p in sorted(directory.glob("*.md"))}


def test_architecture_prose_counts_as_structure():
    """Dataflow language is structure even with no arrow and no causal term."""
    pages = _pages("aiayn-live")
    stack = pages["encoder-decoder-stack"]

    assert structural_signals(stack) >= DIAGRAM_SIGNAL_FLOOR
    assert any("mermaid" in p for p in pedagogy_problems(stack, "encoder-decoder-stack"))


def test_the_transformer_paper_is_not_uniformly_flagged():
    """A gate that fires everywhere is as useless as one that never fires."""
    pages = _pages("aiayn-live")
    flagged = [k for k, md in pages.items()
               if structural_signals(md) >= DIAGRAM_SIGNAL_FLOOR]

    assert 0 < len(flagged) < len(pages) / 2
    assert "encoder-decoder-stack" in flagged


def test_planted_backdoors_are_not_backdoor_paths():
    """The security paper's pages must not be dragged in by the homonym."""
    pages = _pages("p2205.06900-live")
    flagged = [k for k, md in pages.items()
               if structural_signals(md) >= DIAGRAM_SIGNAL_FLOOR]

    assert flagged == []


def test_an_empirical_paper_is_not_asked_for_diagrams():
    """The privacy paper argues from measurements, not from structure."""
    pages = _pages("p2504.04033-live")

    assert all(structural_signals(md) < DIAGRAM_SIGNAL_FLOOR for md in pages.values())


@pytest.mark.parametrize("page_id,expected", [
    ("machine-translation-results", True),
    ("experiments", True),
    ("sid-vs-shd-simulation", True),
    ("model-variations", True),
    ("dag-terminology", False),
    ("graph-comparison-problem", False),   # "comparison" in prose, not results
    ("attention-mechanism", False),
    # Substring matching made theory and method pages owe six numbers. None of
    # the four builds on disk contains one, so only a paper outside them --
    # a diffusion or variational-inference paper -- would ever have shown it.
    ("variational-lower-bound", False),    # "variation" inside "variational"
    ("variational-inference", False),
    ("simulation-based-inference", False),  # a method, not a simulation study
])
def test_results_pages_are_identified_by_their_own_title(page_id, expected):
    assert is_results_page(page_id) is expected


def test_a_results_page_without_figures_is_a_problem():
    prose = "The method performs better than the baseline across every setting."

    problems = pedagogy_problems(prose, "experiments")

    assert any("reports results" in p for p in problems)


def test_a_results_page_carrying_its_table_passes():
    pages = _pages("p2504.04033-live")
    carried = pages["disparity-inference-performance"]

    assert figure_count(carried) >= 6
    assert not any("reports results" in p
                   for p in pedagogy_problems(carried, "disparity-inference-performance"))


def test_figures_inside_code_blocks_do_not_count():
    """A listing full of line numbers is not a results table."""
    fenced = "Results were strong.\n\n```python\nx = 3.14159\ny = 2.71828\nz = 1.41421\n```\n"

    assert figure_count(fenced) == 0


def test_an_over_long_paragraph_is_quoted_not_just_numbered():
    """The retry loop feeds these strings straight back to the writer as its
    only correction. "prose paragraph 8 exceeds 100 words" tells it that it
    failed but not which text to cut -- the writer does not index paragraphs
    the way prose_word_counts does, so it has to guess, and on
    attention-visualization it guessed wrong three times in a row and the page
    was abandoned. Quoting the opening words makes the target unambiguous.
    """
    from paper_skill.pedagogy import pedagogy_problems

    page = ("## Mechanics {#mechanics}\n\nShort one [eq_1].\n\n"
            + "The attention heads resolve anaphora across long distances "
            + " ".join(["filler"] * 100) + " [§sec_8].\n")

    problem = next(p for p in pedagogy_problems(page) if "exceeds 100" in p)

    assert "The attention heads resolve anaphora" in problem


def test_the_60_word_ratio_names_which_paragraphs():
    """Half-fixing the feedback left the same hole one threshold down. With the
    100-word problems quoted, attention-visualization stopped tripping them and
    landed on "4/19 prose paragraphs exceed 60 words" -- which again names no
    paragraph, so the writer split the page into 19 and still left 4 long.
    """
    from paper_skill.pedagogy import pedagogy_problems

    long_one = "Anaphora resolution spans the whole sentence " + " ".join(
        ["filler"] * 60)
    page = "## Mechanics {#mechanics}\n\n" + "Short [eq_1].\n\n" * 3 + long_one

    problem = next(p for p in pedagogy_problems(page) if "exceed 60" in p)

    assert "Anaphora resolution spans the whole sentence" in problem
