"""[[Concept Name]] reached the reader as literal brackets.

The writing contract never asks for wiki links -- the model produces them out
of habit -- so they appear sporadically rather than everywhere: six across the
four builds on disk, written both as a label and as an id. Rewritten at build
time into ordinary markdown links, which the renderer already handles, so no
component has to learn a second link syntax.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from build_data import resolve_wiki_links  # noqa: E402

NODES = [
    {"id": "encoder-decoder-stack", "label": "Encoder and Decoder Stacks"},
    {"id": "structural-intervention-distance",
     "label": "Structural Intervention Distance (SID)"},
    {"id": "sdpa", "label": "Scaled Dot-Product Attention"},
]


def test_a_label_becomes_a_link_to_its_concept():
    out = resolve_wiki_links(
        "the Transformer's [[Encoder and Decoder Stacks]] rely on it", NODES)

    assert out == ("the Transformer's [Encoder and Decoder Stacks]"
                   "(#encoder-decoder-stack) rely on it")


def test_an_id_resolves_too_and_is_shown_by_its_label():
    """The SID build wrote the id. A reader should never be shown a slug."""
    out = resolve_wiki_links("see [[structural-intervention-distance]] for more",
                             NODES)

    assert out == ("see [Structural Intervention Distance (SID)]"
                   "(#structural-intervention-distance) for more")


def test_a_name_that_matches_nothing_loses_its_brackets():
    """A link to a concept that does not exist would scroll nowhere. The words
    are still the author's, so they stay -- only the markup goes."""
    out = resolve_wiki_links("compare with [[Some Other Paper]] here", NODES)

    assert out == "compare with Some Other Paper here"


def test_matching_ignores_case_and_surrounding_space():
    out = resolve_wiki_links("[[ scaled dot-product attention ]]", NODES)

    assert out == "[Scaled Dot-Product Attention](#sdpa)"


def test_several_links_in_one_paragraph_all_resolve():
    out = resolve_wiki_links("[[sdpa]] feeds [[Encoder and Decoder Stacks]]", NODES)

    assert out.count("](#") == 2


def test_brackets_inside_a_code_fence_are_left_alone():
    """A fenced block can hold anything -- LaTeX, pseudocode, a nested index --
    and rewriting inside it would corrupt the code the reader is shown."""
    text = ("prose [[sdpa]] here\n\n```python\nweights[[i]] = 1\n```\n\n"
            "more [[sdpa]]")

    out = resolve_wiki_links(text, NODES)

    assert "weights[[i]] = 1" in out
    assert out.count("](#sdpa)") == 2


def test_display_math_is_left_alone():
    out = resolve_wiki_links("$$A_{[[i]]}$$", NODES)

    assert out == "$$A_{[[i]]}$$"


def test_a_page_with_no_wiki_links_is_returned_unchanged():
    text = "Ordinary prose with [a real link](https://example.test)."

    assert resolve_wiki_links(text, NODES) == text
