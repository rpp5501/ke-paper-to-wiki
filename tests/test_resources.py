"""Resource verification: the cited id must BE the cited paper.

The two mismatches pinned below are real. They were produced by the live P3
stage, shipped into the backdoor-attack build, and both return HTTP 200 -- a
reachability check passes them. One of them cites a fashion-recommendation
paper on a page about backdoor defenses.
"""
import pytest

from paper_skill.resources import titles_agree, verify_resources

NEURAL_CLEANSE = ("Neural Cleanse: Identifying and Mitigating Backdoor Attacks "
                  "in Neural Networks (Wang et al., IEEE S&P 2019)")
STRIP = "STRIP: A Defence Against Trojan Attacks on Deep Neural Networks"
BENCHMARK = ("A Benchmark Study of Backdoor Data Poisoning Defenses for Deep "
             "Neural Network Classifiers and A Novel Defense")
FASHION = ("Personalized Fashion Recommendation from Personal Social Media "
           "Data: An Item-to-Set Metric Learning Approach")

ATOM = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">{entries}</feed>"""
ENTRY = """<entry><id>http://arxiv.org/abs/{aid}v1</id><title>{title}</title></entry>"""


class _Resp:
    def __init__(self, content):
        self.content = content.encode("utf-8")

    def raise_for_status(self):
        pass


def _arxiv(**titles):
    """A fake arXiv API returning exactly the ids it is given, and no others."""
    def get(_url, params=None, **_kw):
        wanted = (params or {}).get("id_list", "").split(",")
        entries = "".join(ENTRY.format(aid=a, title=t)
                          for a, t in titles.items() if a in wanted)
        return _Resp(ATOM.format(entries=entries))
    return get


def _head(status=200):
    class R:
        status_code = status
    return lambda *_a, **_kw: R()


def _note(*resources):
    return {"concept": "c", "resources": list(resources)}


# --- title comparison -------------------------------------------------------

def test_a_real_mismatch_is_caught():
    assert not titles_agree(NEURAL_CLEANSE, STRIP)
    assert not titles_agree(BENCHMARK, FASHION)


@pytest.mark.parametrize("claimed,actual", [
    ("Attention Is All You Need", "Attention Is All You Need"),
    # The usual citation form: the real title with an author tail appended.
    ("Attention Is All You Need (Vaswani et al., 2017)", "Attention Is All You Need"),
    # Case and punctuation are not differences.
    ("attention is all you need!", "Attention Is All You Need"),
    # A dropped subtitle still names the same work.
    ("BERT: Pre-training of Deep Bidirectional Transformers",
     "BERT: Pre-training of Deep Bidirectional Transformers for Language "
     "Understanding"),
])
def test_correct_citations_are_not_flagged(claimed, actual):
    assert titles_agree(claimed, actual)


def test_an_absent_title_is_not_treated_as_a_fault():
    """Nothing to compare is not evidence of a wrong citation."""
    assert titles_agree("", "Attention Is All You Need")


# --- the gate ---------------------------------------------------------------

def test_the_shipped_wrong_paper_is_rejected():
    note = _note({"url": "https://arxiv.org/abs/1902.06531",
                  "title": NEURAL_CLEANSE, "type": "follow-up-paper"})

    problems = verify_resources(note, get=_arxiv(**{"1902.06531": STRIP}),
                                head=_head())

    assert len(problems) == 1
    assert "1902.06531" in problems[0] and "STRIP" in problems[0]


def test_a_correct_citation_passes():
    note = _note({"url": "https://arxiv.org/abs/1706.03762",
                  "title": "Attention Is All You Need (Vaswani et al., 2017)"})

    assert verify_resources(
        note, get=_arxiv(**{"1706.03762": "Attention Is All You Need"}),
        head=_head()) == []


def test_an_id_arxiv_does_not_know_is_reported():
    note = _note({"url": "https://arxiv.org/abs/2999.99999", "title": "Whatever"})

    problems = verify_resources(note, get=_arxiv(), head=_head())

    assert problems == ["arXiv:2999.99999 does not resolve to a paper"]


def test_every_bad_citation_is_reported_not_just_the_first():
    """One round of feedback should carry all of them; the retry gets one shot."""
    note = _note({"url": "https://arxiv.org/abs/1902.06531", "title": NEURAL_CLEANSE},
                 {"url": "https://arxiv.org/abs/2005.12439", "title": BENCHMARK})

    problems = verify_resources(
        note, get=_arxiv(**{"1902.06531": STRIP, "2005.12439": FASHION}),
        head=_head())

    assert len(problems) == 2


# --- non-arXiv reachability -------------------------------------------------

def test_a_dead_page_is_reported():
    note = _note({"url": "https://example.edu/gone.pdf", "title": "T"})

    assert verify_resources(note, get=_arxiv(), head=_head(404)) == [
        "https://example.edu/gone.pdf returns 404"]


def test_a_host_refusing_the_probe_is_not_a_dead_link():
    """Publishers and university sites routinely 403 an unknown agent. Treating
    that as a missing page would reject good resources."""
    note = _note({"url": "https://example.edu/paper.pdf", "title": "T"})

    assert verify_resources(note, get=_arxiv(), head=_head(403)) == []


def test_an_unreachable_host_is_reported():
    def boom(*_a, **_kw):
        raise OSError("name or service not known")

    note = _note({"url": "https://people.cs.uchicago.edu/~x/backdoor.pdf", "title": "T"})

    problems = verify_resources(note, get=_arxiv(), head=boom)

    assert problems == ["https://people.cs.uchicago.edu/~x/backdoor.pdf is unreachable"]


# --- staying out of the way -------------------------------------------------

def test_a_note_with_no_resources_has_no_problems():
    assert verify_resources({"concept": "c"}) == []


def test_the_api_kill_switch_silences_the_gate(monkeypatch):
    """RESEARCH_MCP_NO_APIS=1 means offline on purpose. Unverifiable is not
    wrong, and failing every note would make the pipeline unusable."""
    monkeypatch.setenv("RESEARCH_MCP_NO_APIS", "1")
    note = _note({"url": "https://arxiv.org/abs/1902.06531", "title": NEURAL_CLEANSE})

    assert verify_resources(note, get=_arxiv(), head=_head()) == []


def test_a_broken_verifier_does_not_read_as_a_broken_note():
    def boom(*_a, **_kw):
        raise ConnectionError("arxiv down")

    note = _note({"url": "https://arxiv.org/abs/1706.03762", "title": "T"})

    problems = verify_resources(note, get=boom, head=_head())

    assert len(problems) == 1
    assert "could not reach arXiv" in problems[0]
