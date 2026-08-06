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
