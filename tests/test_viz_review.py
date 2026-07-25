"""R13.1 — viz placement (anchor_tier) + the bounded critique loop.

Patterns adopted from llmsresearch/paperbanana (MIT, checked 2026-07-24):
a written style-guidelines file the critic must cite, a hard iteration cap
instead of "until satisfied", and their faithfulness/conciseness/readability
split as review checklist headings rather than a second LLM judge.
"""
import json
from pathlib import Path

import pytest

from paper_skill.viz import (
    ANCHOR_TIERS,
    MAX_REVIEWS,
    gate_viz_dir,
    load_manifest,
    main,
    review_packet,
    write_viz,
)


@pytest.fixture
def page(tmp_path):
    p = tmp_path / "04_sdpa.md"
    p.write_text(
        "# SDPA\n\n## Intuition {#intuition}\n\nA dot product scores.\n\n"
        "## The Math {#the-math}\n\nDivide by sqrt(dk).\n",
        encoding="utf-8",
    )
    return p


def _write(tmp_path, page, **overrides):
    kwargs = dict(
        title="t", caption="c", prompt="bet?", page_path=page,
        generated="2026-07-17",
    )
    kwargs.update(overrides)
    return write_viz(tmp_path / "viz", "sdpa", "attention-heatmap",
                     {"a": 1}, **kwargs)


# ── placement ────────────────────────────────────────────────────────────
def test_anchor_tier_defaults_to_after_intuition(tmp_path, page):
    assert _write(tmp_path, page)["anchor_tier"] == "after-intuition"


def test_anchor_tier_can_be_placed_in_the_math(tmp_path, page):
    entry = _write(tmp_path, page, anchor_tier="in-the-math")
    assert entry["anchor_tier"] == "in-the-math"
    assert load_manifest(tmp_path / "viz")["sdpa"]["anchor_tier"] == "in-the-math"


def test_an_unknown_anchor_tier_is_refused(tmp_path, page):
    with pytest.raises(ValueError, match="anchor_tier"):
        _write(tmp_path, page, anchor_tier="in-the-footnotes")


def test_the_gate_rejects_a_hand_edited_anchor_tier(tmp_path, page):
    _write(tmp_path, page)
    viz = tmp_path / "viz"
    manifest = load_manifest(viz)
    manifest["sdpa"]["anchor_tier"] = "somewhere-else"
    (viz / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    assert any("anchor_tier" in f for f in gate_viz_dir(viz))


def test_build_pack_carries_anchor_tier_from_the_params_json(tmp_path, page):
    from paper_skill.viz import build_pack

    findings = build_pack({"sdpa": {
        "template_id": "attention-heatmap", "title": "t", "caption": "c",
        "prompt": "bet?", "page": page.name, "anchor_tier": "in-the-math",
        "params": {"a": 1}}}, page.parent, tmp_path / "viz")

    assert findings == []
    assert load_manifest(tmp_path / "viz")["sdpa"]["anchor_tier"] == "in-the-math"


def test_the_known_tiers_are_the_two_designed_slots():
    assert ANCHOR_TIERS == ("after-intuition", "in-the-math")


# ── bounded critique loop ────────────────────────────────────────────────
def test_review_packet_carries_the_page_and_the_current_params(tmp_path, page):
    _write(tmp_path, page)

    packet = review_packet(tmp_path / "viz", "sdpa", page.parent)

    assert "Divide by sqrt(dk)" in packet["page_text"]
    assert packet["params"] == {"a": 1}
    assert packet["node_id"] == "sdpa"


def test_review_packet_cites_the_written_guidelines(tmp_path, page):
    _write(tmp_path, page)

    packet = review_packet(tmp_path / "viz", "sdpa", page.parent)

    # paperbanana's discipline: the critic argues from a written style guide,
    # not from taste.
    assert "GUIDELINES.md" in packet["guidelines_path"]
    assert packet["guidelines"].strip(), "guidelines file must not be empty"


def test_review_packet_uses_the_rubric_as_checklist_headings(tmp_path, page):
    _write(tmp_path, page)

    packet = review_packet(tmp_path / "viz", "sdpa", page.parent)

    assert packet["checklist"] == ("faithfulness", "conciseness", "readability")


def test_review_is_params_only(tmp_path, page):
    _write(tmp_path, page)

    packet = review_packet(tmp_path / "viz", "sdpa", page.parent)

    assert packet["editable"] == ("params", "prompt", "caption")
    assert "srcdoc" not in packet
    assert "html" not in packet


def test_review_counts_up_and_stops_at_the_cap(tmp_path, page):
    _write(tmp_path, page)
    viz = tmp_path / "viz"

    for expected in range(1, MAX_REVIEWS + 1):
        packet = review_packet(viz, "sdpa", page.parent)
        assert packet["review_count"] == expected

    # A bounded loop, not "until satisfied".
    with pytest.raises(ValueError, match="review cap"):
        review_packet(viz, "sdpa", page.parent)


def test_the_cap_is_two(tmp_path, page):
    assert MAX_REVIEWS == 2


def test_cli_review_prints_the_checklist_and_the_cap(tmp_path, page, capsys):
    _write(tmp_path, page)

    code = main(["review", "sdpa", "--viz-dir", str(tmp_path / "viz"),
                 "--pages-dir", str(page.parent)])

    out = capsys.readouterr().out
    assert code == 0
    for heading in ("faithfulness", "conciseness", "readability"):
        assert heading in out
    assert "1 of 2" in out
    assert "params" in out  # params-only scope is stated up front


def test_cli_review_refuses_past_the_cap(tmp_path, page, capsys):
    _write(tmp_path, page)
    args = ["review", "sdpa", "--viz-dir", str(tmp_path / "viz"),
            "--pages-dir", str(page.parent)]
    for _ in range(MAX_REVIEWS):
        assert main(args) == 0

    assert main(args) == 1
    assert "review cap" in capsys.readouterr().out


def test_reviewing_an_unknown_node_is_refused(tmp_path, page):
    _write(tmp_path, page)

    with pytest.raises(KeyError, match="ghost"):
        review_packet(tmp_path / "viz", "ghost", page.parent)
