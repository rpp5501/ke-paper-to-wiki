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


# --- educational composition -------------------------------------------------
# Across every note the three aman.ai papers produced, the model chose only
# papers and code: 7 resources, zero `visual`, zero `lecture`. The type
# vocabulary offered both. Verified, relevant, and still not what a learner
# wants -- the sources are not bad, a whole category is simply missing.

def _typed_note(*types):
    return {"concept": "c", "status": "complete",
            "resources": [{"url": f"https://x/{i}", "title": f"t{i}",
                           "type": t, "why": "w"} for i, t in enumerate(types)]}


def test_a_note_of_only_papers_and_code_reports_the_gap():
    from paper_skill.resources import educational_gap

    problems = educational_gap(_typed_note("follow-up-paper", "reference-impl"))

    assert problems and "visual" in problems[0] and "lecture" in problems[0]


def test_one_visual_satisfies_the_floor():
    from paper_skill.resources import educational_gap

    assert educational_gap(_typed_note("follow-up-paper", "visual")) == []


def test_one_lecture_satisfies_the_floor():
    from paper_skill.resources import educational_gap

    assert educational_gap(_typed_note("lecture", "reference-impl")) == []


def test_a_note_with_no_resources_is_lint_notes_business_not_ours():
    """Reporting a missing explainer on a note that has no resources at all
    buries the real fault under a second one."""
    from paper_skill.resources import educational_gap

    assert educational_gap({"concept": "c", "resources": []}) == []
    assert educational_gap(None) == []


# --- youtube -----------------------------------------------------------------
# Asking for lectures makes video the one resource type the existing checks
# cannot see. youtube.com/watch?v=<anything> answers 200 with a "Video
# unavailable" page, so a real channel with an invented id passes the dead-link
# check exactly like a real video. oEmbed is the cheap discriminator: it 404s
# on an id that does not exist.

def _oembed(known=("DAOcjicFr1Y",)):
    class R:
        def __init__(self, code): self.status_code = code
    def head(url, **_kw):
        if "oembed" in url:
            return R(200 if any(k in url for k in known) else 404)
        return R(200)
    return head


def test_an_invented_video_id_is_caught():
    note = _note({"url": "https://www.youtube.com/watch?v=zzzFAKEzzz1",
                  "title": "Lecture", "type": "lecture"})

    problems = verify_resources(note, get=_arxiv(), head=_oembed())

    assert len(problems) == 1 and "youtube" in problems[0].lower()


def test_a_real_video_passes():
    note = _note({"url": "https://www.youtube.com/watch?v=DAOcjicFr1Y",
                  "title": "Lecture", "type": "lecture"})

    assert verify_resources(note, get=_arxiv(), head=_oembed()) == []


def test_the_short_youtu_be_form_is_checked_too():
    note = _note({"url": "https://youtu.be/zzzFAKEzzz1", "title": "L",
                  "type": "lecture"})

    assert verify_resources(note, get=_arxiv(), head=_oembed())


# --- embed_kind ---------------------------------------------------------
# Build-time classification so the dashboard never has to fetch these urls
# itself: an image renders inline, a YouTube link renders as its thumbnail,
# everything else stays a plain link.

def _probe(status=200, content_type=""):
    class R:
        status_code = status
        headers = {"Content-Type": content_type}
    return lambda *_a, **_kw: R()


def test_an_image_content_type_is_embedded():
    from paper_skill.resources import embed_kind

    assert embed_kind("https://x/plot.png", head=_probe(200, "image/png")) == {
        "kind": "image", "src": "https://x/plot.png"}


def test_image_content_type_tolerates_charset_and_case():
    """content-type is matched on prefix, not exact string, so a real server's
    'Image/PNG; charset=binary' still counts."""
    from paper_skill.resources import embed_kind

    kind = embed_kind("https://x/plot.png", head=_probe(200, "Image/PNG; charset=x"))

    assert kind["kind"] == "image"


def test_an_html_page_is_a_link():
    from paper_skill.resources import embed_kind

    assert embed_kind("https://x/page.html", head=_probe(200, "text/html")) == {
        "kind": "link"}


@pytest.mark.parametrize("url,vid", [
    ("https://www.youtube.com/watch?v=DAOcjicFr1Y", "DAOcjicFr1Y"),
    ("https://youtu.be/DAOcjicFr1Y", "DAOcjicFr1Y"),
    ("https://www.youtube.com/embed/DAOcjicFr1Y", "DAOcjicFr1Y"),
])
def test_each_youtube_url_form_is_a_video_with_no_network_call(url, vid):
    """The thumbnail url is derived from the video id -- no HEAD needed, so a
    `head` that would raise if called must never be called."""
    from paper_skill.resources import embed_kind

    def boom(*_a, **_kw):
        raise AssertionError("embed_kind must not probe a YouTube url")

    assert embed_kind(url, head=boom) == {
        "kind": "video",
        "src": f"https://img.youtube.com/vi/{vid}/hqdefault.jpg",
        "href": url}


def test_a_head_that_raises_is_a_link_not_an_exception():
    """Same precedent as verify_resources: a checker that cannot reach the
    host must never claim the resource is broken."""
    from paper_skill.resources import embed_kind

    def boom(*_a, **_kw):
        raise OSError("no route to host")

    assert embed_kind("https://example.edu/thing", head=boom) == {"kind": "link"}


def test_a_non_2xx_status_is_a_link():
    from paper_skill.resources import embed_kind

    assert embed_kind("https://x/plot.png", head=_probe(404, "image/png")) == {
        "kind": "link"}


@pytest.mark.parametrize("url", ["", "mailto:a@b.com"])
def test_a_non_http_url_is_a_link(url):
    from paper_skill.resources import embed_kind

    def boom(*_a, **_kw):
        raise AssertionError("must not probe a non-http url")

    assert embed_kind(url, head=boom) == {"kind": "link"}


# --- embed_kind: id extraction is structural, not "first v= anywhere" ------
# A v= embedded in an unrelated query value (e.g. a next= redirect target)
# must never win over the real id -- that silently produces a wrong
# thumbnail instead of degrading to a plain link, which is worse than failing.

def _no_probe(*_a, **_kw):
    raise AssertionError("embed_kind must not probe a YouTube url")


def test_an_earlier_unrelated_v_param_does_not_win():
    """REALID12 is only 8 characters -- not a real id shape either -- so the
    contract-honest outcome is `link`, not a thumbnail for either candidate.
    What must never happen is picking FAKEID because it appears first."""
    from paper_skill.resources import embed_kind

    url = ("https://www.youtube.com/watch?next=https://example.com"
           "?v=FAKEID&v=REALID12")

    kind = embed_kind(url, head=_no_probe)

    assert "FAKEID" not in kind.get("src", "")
    assert kind == {"kind": "link"}


def test_a_real_id_after_an_unrelated_v_param_is_still_extracted():
    from paper_skill.resources import embed_kind

    url = ("https://www.youtube.com/watch?next=https://example.com"
           "?v=FAKEID&v=dQw4w9WgXcQ")

    assert embed_kind(url, head=_no_probe) == {
        "kind": "video",
        "src": "https://img.youtube.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
        "href": url}


def test_a_playlist_embed_has_no_single_video_id():
    """/embed/videoseries is a playlist -- 'videoseries' is not a video id."""
    from paper_skill.resources import embed_kind

    assert embed_kind("https://www.youtube.com/embed/videoseries?list=PLabc",
                       head=_no_probe) == {"kind": "link"}


def test_id_not_first_in_the_query_string_still_works():
    from paper_skill.resources import embed_kind

    url = "https://www.youtube.com/watch?feature=share&v=dQw4w9WgXcQ"

    assert embed_kind(url, head=_no_probe) == {
        "kind": "video",
        "src": "https://img.youtube.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
        "href": url}


@pytest.mark.parametrize("url", [
    "https://youtu.be/dQw4w9WgXcQ?si=abc123",
    "https://youtu.be/dQw4w9WgXcQ?si=abc123&t=30s",
])
def test_tracking_suffixes_on_the_short_form_do_not_break_extraction(url):
    from paper_skill.resources import embed_kind

    assert embed_kind(url, head=_no_probe) == {
        "kind": "video",
        "src": "https://img.youtube.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
        "href": url}


@pytest.mark.parametrize("vid", ["short1234", "toolongbyonecharacter1"])
def test_a_malformed_length_id_degrades_to_a_link(vid):
    from paper_skill.resources import embed_kind

    assert embed_kind(f"https://www.youtube.com/watch?v={vid}",
                       head=_no_probe) == {"kind": "link"}


def test_an_id_with_a_trailing_newline_degrades_to_a_link():
    """`$` also matches just before a single trailing newline, so an
    eleven-character id shape check anchored with `$` lets a `%0A`-suffixed
    query value slip through and leak a literal newline into the thumbnail
    url. It must degrade to a link like any other malformed id."""
    from paper_skill.resources import embed_kind

    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ%0A"

    assert embed_kind(url, head=_no_probe) == {"kind": "link"}


# --- arxiv rate limiting -----------------------------------------------------
# Enrichment took P3 from ~1 concept per paper to 10-14, and lottery-ticket then
# lost 4 of its 6 failed notes to "could not reach arXiv to verify N
# citation(s): 429 Too Many Requests" / 503. The note was fine; we simply asked
# arXiv too fast. Reporting the verifier's own failure rather than blaming the
# note is right, but losing the note to it is not -- it is a transient, and
# llm_spawn already treats transients as worth one backoff.

class _Flaky:
    """Fails with `code` for the first `fails` calls, then succeeds."""

    def __init__(self, fails, code=429, body=None):
        self.fails, self.code, self.calls = fails, code, 0
        self.body = body or ATOM.format(
            entries=ENTRY.format(aid="1706.03762", title="Attention Is All You Need"))

    def __call__(self, _url, params=None, **_kw):
        self.calls += 1
        if self.calls <= self.fails:
            import requests
            raise requests.HTTPError(f"{self.code} Client Error")
        return _Resp(self.body)


def test_a_rate_limited_arxiv_call_is_retried():
    from paper_skill.resources import arxiv_titles
    flaky = _Flaky(fails=1)

    titles = arxiv_titles(["1706.03762"], get=flaky, sleep=lambda _s: None)

    assert titles == {"1706.03762": "Attention Is All You Need"}
    assert flaky.calls == 2, "expected one retry after the 429"


def test_retries_are_bounded():
    """A permanently unreachable arXiv must not retry forever; the caller
    turns the raised error into "could not reach arXiv", blaming the verifier
    rather than the note."""
    import pytest as _pytest
    from paper_skill.resources import arxiv_titles, ARXIV_ATTEMPTS
    flaky = _Flaky(fails=99)

    with _pytest.raises(Exception):
        arxiv_titles(["1706.03762"], get=flaky, sleep=lambda _s: None)

    assert flaky.calls == ARXIV_ATTEMPTS


# --- embed_kind: og:image preview for visual explainers --------------------
# 42 resources across the built papers are typed `visual` -- distill.pub, Jay
# Alammar, an author's own post -- and every one of them rendered as a bare
# link, identical to a follow-up paper. The type promises a picture and the
# page shows a line of blue text. These hosts publish an og:image; one GET
# turns the promise into the preview card the renderer already knows how to
# draw. Opt-in, because a wall of arXiv social cards on every follow-up-paper
# is worse than the plain links they are today.

def _page(body, status=200, content_type="text/html"):
    class R:
        status_code = status
        headers = {"Content-Type": content_type}
        text = body
    return lambda *_a, **_kw: R()


def _head_by_suffix(*_a, **_kw):
    """A head that tells pages from images, so the og:image confirmation step
    has something real to check. Used by the preview tests below."""
    url = _a[0] if _a else _kw.get("url", "")
    class R:
        status_code = 200
        headers = {"Content-Type":
                   "image/png" if url.rsplit("?", 1)[0].endswith(
                       (".png", ".jpg", ".jpeg", ".gif", ".svg"))
                   else "text/html"}
    return R()


OG = ('<html><head><meta property="og:image" '
      'content="https://distill.pub/2020/card.png"></head></html>')


def test_a_visual_explainer_becomes_a_preview_card():
    from paper_skill.resources import embed_kind

    kind = embed_kind("https://distill.pub/2020/x/", head=_head_by_suffix,
                      get=_page(OG), want_preview=True)

    assert kind == {"kind": "image", "src": "https://distill.pub/2020/card.png"}


def test_the_page_is_not_fetched_unless_a_preview_was_asked_for():
    """Default behaviour is byte-identical to before: one HEAD, no GET."""
    from paper_skill.resources import embed_kind

    def boom(*_a, **_kw):
        raise AssertionError("embed_kind must not GET without want_preview")

    assert embed_kind("https://distill.pub/2020/x/",
                      head=_probe(200, "text/html"), get=boom) == {"kind": "link"}


def test_a_page_with_no_og_image_stays_a_link():
    from paper_skill.resources import embed_kind

    kind = embed_kind("https://x/page.html", head=_probe(200, "text/html"),
                      get=_page("<html><head><title>t</title></head></html>"),
                      want_preview=True)

    assert kind == {"kind": "link"}


def test_a_relative_og_image_is_resolved_against_the_page():
    """Real pages ship '/img/card.png'. Handing that to an <img src> in the
    dashboard resolves it against the dashboard's own origin and 404s."""
    from paper_skill.resources import embed_kind

    kind = embed_kind(
        "https://jalammar.github.io/illustrated-transformer/",
        head=_head_by_suffix,
        get=_page('<meta property="og:image" content="/img/card.png">'),
        want_preview=True)

    assert kind["src"] == "https://jalammar.github.io/img/card.png"


def test_a_failing_get_degrades_to_a_link_not_an_error():
    """Same precedent as the HEAD path: this function never turns a resource
    into a build failure, it only declines to promote it."""
    from paper_skill.resources import embed_kind

    def boom(*_a, **_kw):
        raise RuntimeError("network")

    assert embed_kind("https://x/page.html", head=_probe(200, "text/html"),
                      get=boom, want_preview=True) == {"kind": "link"}


def test_a_direct_image_url_still_skips_the_preview_fetch():
    """An image is already an image -- want_preview must not add a GET."""
    from paper_skill.resources import embed_kind

    def boom(*_a, **_kw):
        raise AssertionError("no GET needed for a direct image")

    assert embed_kind("https://x/plot.png", head=_probe(200, "image/png"),
                      get=boom, want_preview=True) == {
        "kind": "image", "src": "https://x/plot.png"}


# --- og:image previews: what a real probe of the built papers turned up -----
# Running this against the 27 real `visual` urls in the six built bundles,
# 14 "worked" and several were wrong in ways no fixture caught:
#   jacobgil.github.io  -> og:image is "http://jacobgil.github.io", the site
#                          root, not an image -- a broken <img> in the page
#   arxiv.org           -> the arXiv logo
#   paperswithcode.com  -> a Hugging Face "trending papers" thumbnail
# A generic site-wide card is worse than the plain link it replaces: it
# occupies the space of a diagram and shows the reader nothing about the idea.

GENERIC_HOSTS_SAMPLE = [
    ("https://arxiv.org/abs/1803.03635",
     "https://arxiv.org/static/browse/0.3.4/images/arxiv-logo-fb.png"),
    ("https://paperswithcode.com/method/lottery-ticket-hypothesis",
     "https://huggingface.co/front/thumbnails/trending-papers.png"),
    ("https://github.com/samuela/git-re-basin",
     "https://opengraph.githubassets.com/592d/samuela/git-re-basin"),
]


@pytest.mark.parametrize("page_url,og", GENERIC_HOSTS_SAMPLE)
def test_a_host_with_a_generic_social_card_stays_a_link(page_url, og):
    from paper_skill.resources import embed_kind

    kind = embed_kind(page_url, head=_probe(200, "text/html"),
                      get=_page(f'<meta property="og:image" content="{og}">'),
                      want_preview=True)

    assert kind == {"kind": "link"}


def test_an_og_image_that_is_not_an_image_is_rejected():
    """jacobgil.github.io advertises its own site root as its og:image.
    Trusting the tag would put a broken <img> on the page."""
    from paper_skill.resources import embed_kind

    kind = embed_kind("https://jacobgil.github.io/deeplearning/pruning",
                      head=_head_by_suffix,
                      get=_page('<meta property="og:image" '
                                'content="http://jacobgil.github.io">'),
                      want_preview=True)

    assert kind == {"kind": "link"}


def test_a_real_content_image_survives_the_extra_check():
    """distill.pub's per-article thumbnail is exactly what this is for."""
    from paper_skill.resources import embed_kind

    kind = embed_kind("https://distill.pub/2017/momentum/", head=_head_by_suffix,
                      get=_page('<meta property="og:image" '
                                'content="http://distill.pub/2017/momentum/thumbnail.jpg">'),
                      want_preview=True)

    # Upgraded to https on the way out -- see the mixed-content test below.
    assert kind == {"kind": "image",
                    "src": "https://distill.pub/2017/momentum/thumbnail.jpg"}


# A refused probe is not a missing image -- the _DEAD_STATUS precedent again,
# in the og:image confirmation step. Probing the real urls: Wikipedia answered
# 429 and Meta's CDN 403 for images that are perfectly real and load fine in a
# browser, while cs.umd.edu's advertised logo.png genuinely 404s. Only the
# last one is evidence of anything.

def _head_status(status, content_type="text/html"):
    class R:
        status_code = status
        headers = {"Content-Type": content_type}
    return lambda *_a, **_kw: R()


@pytest.mark.parametrize("status", [403, 429, 405])
def test_a_refused_probe_on_an_image_shaped_url_still_counts(status):
    from paper_skill.resources import embed_kind

    def head(url, *_a, **_kw):
        return _head_status(200, "text/html")() if url.endswith("/") \
            else _head_status(status)()

    kind = embed_kind("https://en.wikipedia.org/wiki/Noether/", head=head,
                      get=_page('<meta property="og:image" '
                                'content="https://upload.wikimedia.org/a/b.png">'),
                      want_preview=True)

    assert kind == {"kind": "image",
                    "src": "https://upload.wikimedia.org/a/b.png"}


def test_a_404_og_image_is_still_rejected_even_though_it_looks_like_one():
    """cs.umd.edu advertises img/logo.png and the file is not there."""
    from paper_skill.resources import embed_kind

    def head(url, *_a, **_kw):
        return _head_status(200, "text/html")() if url.endswith("/") \
            else _head_status(404)()

    kind = embed_kind("https://www.cs.umd.edu/~tomg/landscapes/", head=head,
                      get=_page('<meta property="og:image" '
                                'content="https://www.cs.umd.edu/img/logo.png">'),
                      want_preview=True)

    assert kind == {"kind": "link"}


def test_a_refused_probe_on_a_url_with_no_image_extension_is_not_trusted():
    """The extension is the only evidence left when the host refuses to
    answer; without it there is nothing to go on."""
    from paper_skill.resources import embed_kind

    def head(url, *_a, **_kw):
        return _head_status(200, "text/html")() if url.endswith("/") \
            else _head_status(403)()

    kind = embed_kind("https://jacobgil.github.io/pruning/", head=head,
                      get=_page('<meta property="og:image" '
                                'content="http://jacobgil.github.io">'),
                      want_preview=True)

    assert kind == {"kind": "link"}


def test_an_http_og_image_on_an_https_page_is_upgraded():
    """distill.pub serves over https but writes its og:image tag as http.
    A browser blocks that as mixed content, so the card renders blank -- the
    one failure mode this whole feature exists to avoid."""
    from paper_skill.resources import embed_kind

    seen = []

    def head(url, *_a, **_kw):
        seen.append(url)
        return _head_status(200, "image/jpeg" if url.endswith(".jpg")
                            else "text/html")()

    kind = embed_kind("https://distill.pub/2017/momentum/", head=head,
                      get=_page('<meta property="og:image" '
                                'content="http://distill.pub/2017/thumb.jpg">'),
                      want_preview=True)

    assert kind == {"kind": "image", "src": "https://distill.pub/2017/thumb.jpg"}
    assert not any(u.startswith("http://") for u in seen), \
        "the http url must not even be probed, let alone shipped"


def test_an_http_image_from_an_http_page_is_left_alone():
    """Only a page that proved https works gets its assets upgraded."""
    from paper_skill.resources import embed_kind

    kind = embed_kind("http://ruder.io/multi-task/", head=_head_by_suffix,
                      get=_page('<meta property="og:image" '
                                'content="http://ruder.io/card.png">'),
                      want_preview=True)

    assert kind == {"kind": "image", "src": "http://ruder.io/card.png"}
