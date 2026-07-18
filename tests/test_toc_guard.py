"""The anti-silent-TOC-fallback guard: a failed extraction must stop the build."""
import pytest

from paper_skill.concepts import (
    ConceptExtractionError, is_toc_graph, require_ok,
)
from paper_skill.llm_spawn import LLMUnavailable, claude_spawn


def test_require_ok_passes_through_a_real_graph():
    ok = {"status": "ok", "graph": {"nodes": [{"id": "x"}]}, "toc": []}
    assert require_ok(ok) is ok


def test_require_ok_raises_on_failed_extraction():
    with pytest.raises(ConceptExtractionError) as e:
        require_ok({"status": "failed-orchestration", "problems": ["boom"]})
    assert "table-of-contents" in str(e.value)
    assert "boom" in str(e.value)


def test_is_toc_graph_flags_section_heading_graph():
    toc = {"nodes": [{"id": "sec_1"}, {"id": "sec_2"}, {"id": "sec_2_1"}],
           "edges": [{"src": "sec_1", "dst": "sec_2", "kind": "prerequisite"}]}
    assert is_toc_graph(toc) is True


def test_is_toc_graph_accepts_a_real_concept_graph():
    real = {"nodes": [{"id": "transformer"}, {"id": "self-attention"}],
            "edges": [{"src": "transformer", "dst": "self-attention",
                       "kind": "builds-on"}]}
    assert is_toc_graph(real) is False


def test_is_toc_graph_flags_empty_graph():
    assert is_toc_graph({"nodes": [], "edges": []}) is True


def test_claude_spawn_is_loud_when_cli_missing(monkeypatch):
    monkeypatch.setattr("paper_skill.llm_spawn.shutil.which", lambda _: None)
    with pytest.raises(LLMUnavailable) as e:
        claude_spawn("hello")
    # names the escape hatch instead of a bare FileNotFoundError
    assert "inject" in str(e.value).lower()
