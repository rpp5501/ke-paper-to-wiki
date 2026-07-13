import json

import pytest
import yaml

from paper_skill.next_steps import synthesize_ideas, lint_ideas, write_outputs


GAPS = [
    {"kind": "unresolved-note", "text": "Why 8 heads?",
     "anchors": {"nodes": ["mha"], "sources": ["mha.yaml"]}},
    {"kind": "paper-limitation", "text": "Future work",
     "anchors": {"nodes": [], "sources": ["§sec_7"]}},
]
GOOD = json.dumps({"ideas": [{
    "title": "Head-count ablation study",
    "rationale": "The paper never justifies 8 heads.",
    "anchors": {"nodes": ["mha"], "sources": ["mha.yaml", "§sec_7"]},
}]})


def test_synthesis_parses_and_lints_clean():
    result = synthesize_ideas(GAPS, spawn=lambda prompt: GOOD)

    assert result["status"] == "ok"
    assert lint_ideas(result["ideas"]) == []


def test_unanchored_idea_fails_lint():
    bad = [{"title": "Vague vibes", "rationale": "...",
            "anchors": {"nodes": [], "sources": []}}]

    problems = lint_ideas(bad)

    assert problems and "unanchored" in problems[0]


def test_node_anchor_is_required():
    bad = [{"title": "Sources only", "rationale": "r",
            "anchors": {"nodes": [], "sources": ["§sec_7"]}}]

    assert any("node anchors" in problem for problem in lint_ideas(bad))


def test_source_anchor_is_required():
    bad = [{"title": "Nodes only", "rationale": "r",
            "anchors": {"nodes": ["mha"], "sources": []}}]

    assert any("source anchors" in problem for problem in lint_ideas(bad))


@pytest.mark.parametrize("missing", ("title", "rationale"))
def test_required_idea_fields_fail_lint(missing):
    idea = {
        "title": "Direction",
        "rationale": "Reason",
        "anchors": {"nodes": ["mha"], "sources": ["mha.yaml"]},
    }
    del idea[missing]

    assert any(missing in problem for problem in lint_ideas([idea]))


@pytest.mark.parametrize("anchor_name", ("nodes", "sources"))
def test_anchor_values_must_be_lists(anchor_name):
    anchors = {"nodes": ["mha"], "sources": ["mha.yaml"]}
    anchors[anchor_name] = "not-a-list"
    idea = {"title": "Direction", "rationale": "Reason", "anchors": anchors}

    assert any(f"{anchor_name} must be a list" in problem
               for problem in lint_ideas([idea]))


def test_synthesis_retries_invalid_json_once():
    responses = iter(["not json", GOOD])
    prompts = []

    result = synthesize_ideas(
        GAPS, spawn=lambda prompt: prompts.append(prompt) or next(responses))

    assert result["status"] == "ok"
    assert len(prompts) == 2
    assert "Previous output invalid" in prompts[1]


def test_synthesis_rejects_non_list_ideas():
    malformed = json.dumps({"ideas": {"title": "not a list"}})

    result = synthesize_ideas(GAPS, spawn=lambda prompt: malformed)

    assert result["status"] == "failed-orchestration"
    assert any("ideas list" in problem for problem in result["problems"])


def test_synthesis_rejects_invented_anchors():
    invented = json.dumps({"ideas": [{
        "title": "Invented direction",
        "rationale": "r",
        "anchors": {"nodes": ["not-a-node"], "sources": ["fake.md"]},
    }]})

    result = synthesize_ideas(GAPS, spawn=lambda prompt: invented)

    assert result["status"] == "failed-orchestration"
    assert any("invented" in problem for problem in result["problems"])


def test_spawn_exception_fails_closed_without_retry():
    calls = []

    def unavailable(prompt):
        calls.append(prompt)
        raise RuntimeError("worker unavailable")

    result = synthesize_ideas(GAPS, spawn=unavailable)

    assert result == {
        "status": "failed-orchestration",
        "problems": ["synthesis worker error: RuntimeError"],
        "ideas": [],
    }
    assert len(calls) == 1


def test_outputs_written(tmp_path):
    result = synthesize_ideas(GAPS, spawn=lambda prompt: GOOD)

    write_outputs(result["ideas"], tmp_path)

    markdown = (tmp_path / "NEXT_STEPS.md").read_text(encoding="utf-8")
    assert markdown.count("Head-count") == 1
    document = yaml.safe_load(
        (tmp_path / "ideas.yaml").read_text(encoding="utf-8"))
    assert document["ideas"][0]["confirmed"] is False


def test_outputs_reject_invalid_ideas(tmp_path):
    bad = [{"title": "Sources only", "rationale": "r",
            "anchors": {"nodes": [], "sources": ["§sec_7"]}}]

    with pytest.raises(ValueError, match="node anchors"):
        write_outputs(bad, tmp_path)

    assert not (tmp_path / "NEXT_STEPS.md").exists()
    assert not (tmp_path / "ideas.yaml").exists()
