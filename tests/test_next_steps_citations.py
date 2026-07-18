from paper_skill.next_steps import forward_gaps


def test_forward_gaps_wrap_citation_walk():
    fake = lambda paper_id, direction, limit=15: {
        "status": "ok",
        "papers": [{"id": "W1", "title": "BERT", "year": 2019}],
    }

    gaps = forward_gaps("arXiv:1706.03762", walk=fake)

    assert gaps[0]["kind"] == "field-follow-up"
    assert gaps[0]["text"] == "BERT"
    assert gaps[0]["anchors"]["sources"] == ["W1"]


def test_disabled_apis_soft_empty():
    fake = lambda paper_id, direction, limit=15: {
        "status": "apis_disabled", "papers": [],
    }

    assert forward_gaps("x", walk=fake) == []
