from paper_skill.next_steps import novelty_briefs
from research_mcp.validate import validate_brief


IDEAS = [
    {"title": "Head-count ablation study", "rationale": "r",
     "anchors": {"nodes": ["mha"], "sources": ["x"]}},
    {"title": "Audio attention", "rationale": "r",
     "anchors": {"nodes": ["attention"], "sources": ["§sec_7"]}},
]


def test_briefs_valid_and_capped():
    briefs = novelty_briefs(IDEAS, top=1)

    assert len(briefs) == 1
    assert briefs[0]["concept"] == "novelty--head-count-ablation-study"
    assert validate_brief(briefs[0]) == []
    assert "been done" in briefs[0]["sub_questions"][0]
