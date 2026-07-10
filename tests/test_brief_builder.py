# tests/test_brief_builder.py
from paper_skill.briefs import build_brief
from research_mcp.validate import validate_brief

GRAPH = {"nodes": [], "edges": [
    {"src": "sdpa", "dst": "attention", "kind": "part-of"},
    {"src": "mha", "dst": "attention", "kind": "part-of"}]}
ROW = {"id": "sdpa", "label": "Scaled Dot-Product Attention", "level": 2,
       "include": True, "research": True,
       "definition": "Attention with 1/sqrt(dk) scaling.",
       "sub_questions": ["Why sqrt(dk)?", "Gradient effect?"]}


def test_brief_validates_and_excludes_siblings():
    brief = build_brief(ROW, GRAPH, content_type="math")
    assert validate_brief(brief) == []
    assert brief["concept"] == "sdpa"
    assert "mha" in brief["do_not_research"]
    assert brief["budget"] == {"searches": 3, "fetches": 3, "api_calls": 2}
