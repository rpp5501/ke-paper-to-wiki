from paper_skill.upgrade import find_arxiv_sibling

class Resp:
    def __init__(self, p): self._p = p
    def raise_for_status(self): pass
    def json(self): return self._p


def test_finds_arxiv_id_from_openalex():
    payload = {"results": [{"ids": {"arxiv": "https://arxiv.org/abs/1706.03762"}}]}
    ax = find_arxiv_sibling("Attention Is All You Need",
                            get=lambda *a, **k: Resp(payload))
    assert ax == "1706.03762"


def test_no_match_returns_none():
    assert find_arxiv_sibling("x", get=lambda *a, **k: Resp({"results": []})) is None


def test_no_apis_returns_none(monkeypatch):
    monkeypatch.setenv("RESEARCH_MCP_NO_APIS", "1")
    assert find_arxiv_sibling("x") is None
