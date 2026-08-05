"""Build-time term harvest for the paper-wide glossary.

The hover mechanism is keyed per concept, so a term used across twenty pages
had to be written into twenty notes. These terms belong to the paper, not to
one of its concepts, and the set of them is knowable once the pages exist --
which is what lets the definitions be generated at build time instead of
needing a model at runtime.
"""
import pytest

from paper_skill.llm_spawn import LLMUnavailable
from paper_skill.terms import define_terms, harvest_terms

PAGES = [
    "A CPDAG represents a Markov equivalence class. The d-separation test "
    "decides it.",
    "Every CPDAG has undirected edges. We compare against SHD, and "
    "d-separation again.",
    "This page mentions SHD once more and a pre-metric.",
]


def test_a_term_in_two_pages_is_harvested():
    assert "CPDAG" in harvest_terms(PAGES, known=set())


def test_a_term_in_one_page_only_is_not():
    """A word used once is not the paper's vocabulary."""
    assert "pre-metric" not in harvest_terms(PAGES, known=set())


def test_hyphenated_lowercase_compounds_are_harvested():
    assert "d-separation" in harvest_terms(PAGES, known=set())


def test_terms_already_defined_are_dropped():
    assert "CPDAG" not in harvest_terms(PAGES, known={"CPDAG"})


def test_notation_inside_math_spans_is_ignored():
    """The macro table already carries notation; $X$ is not a glossary term."""
    pages = ["the value $SHD$ appears here", "and $SHD$ appears here too"]
    assert harvest_terms(pages, known=set()) == []


def test_notation_inside_display_math_is_ignored_too():
    """Measured on the real pages: \\HH and \\CC were harvested as terms
    because a $...$ pattern matches the empty span inside $$...$$ and leaves
    the body exposed."""
    pages = ["text $$\\HH \\CC$$ more", "text $$\\HH \\CC$$ again"]
    assert harvest_terms(pages, known=set()) == []


def test_markdown_scaffolding_is_not_vocabulary():
    """Every page carries the same tier headings, so the structure scored as
    the most frequent 'terms' in the paper: TL, DR, the-math, go-deeper."""
    pages = ["## TL;DR {#tldr}\nx\n## The Math {#the-math}\ny\n"
             "## Go Deeper {#go-deeper}\nz"] * 3
    assert harvest_terms(pages, known=set()) == []


def test_a_fenced_block_is_not_mined_for_terms():
    """Block bodies are code and LaTeX, not prose."""
    pages = ["```algorithm\nlines:\n  - code: \"FOO BAR\"\n```"] * 3
    assert harvest_terms(pages, known=set()) == []


def test_the_order_is_stable():
    """Byte-identical builds: same pages in, same list out."""
    assert harvest_terms(PAGES, known=set()) == harvest_terms(PAGES, known=set())


def test_ordered_by_page_count_then_alphabetically():
    pages = ["AAA BBB", "AAA BBB", "AAA"]
    assert harvest_terms(pages, known=set()) == ["AAA", "BBB"]


def test_no_repeated_terms_yields_an_empty_list_not_a_crash():
    assert harvest_terms(["one page only, nothing repeats"], known=set()) == []


def test_no_pages_at_all_is_empty():
    assert harvest_terms([], known=set()) == []


def test_define_terms_returns_a_definition_per_term():
    def spawn(prompt):
        return '{"CPDAG": "A completed partially directed acyclic graph."}'

    assert define_terms(["CPDAG"], PAGES, spawn) == {
        "CPDAG": "A completed partially directed acyclic graph."}


def test_define_terms_asks_once_for_all_of_them():
    """One batched call, not one call per term."""
    calls = []

    def spawn(prompt):
        calls.append(prompt)
        return '{"CPDAG": "x", "SHD": "y"}'

    define_terms(["CPDAG", "SHD"], PAGES, spawn)
    assert len(calls) == 1


def test_an_unparseable_reply_is_loud():
    """Never a silently empty glossary -- that is indistinguishable from a
    paper whose terms are all already defined."""
    with pytest.raises(LLMUnavailable):
        define_terms(["CPDAG"], PAGES, lambda prompt: "sorry, I cannot")


def test_no_terms_means_no_call_at_all():
    def spawn(prompt):
        raise AssertionError("should not spend tokens on an empty list")

    assert define_terms([], PAGES, spawn) == {}
