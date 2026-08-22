"""Task 3: every note resource gains an `embed` key at build time (Task 2's
`embed_kind` shape), so the dashboard never makes a network call at runtime.

`embed_head` is the injectable network seam (mirrors resources.py's own
`head=` convention); `embed_probe=False` is the offline kill switch that
`--no-embed-probe` drives from the CLI -- it skips embed_kind entirely rather
than merely swapping in a no-op head, so even a YouTube url (which embed_kind
classifies without any network call) still comes out `link`.
"""
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build_data import build_bundle

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = __import__("json").loads(
    (ROOT / "fixtures" / "aiayn_concept_graph.json").read_text(encoding="utf-8"))
NODE_ID = FIXTURE["nodes"][0]["id"]
OTHER_NODE_ID = FIXTURE["nodes"][1]["id"]


def _probe(status=200, content_type=""):
    class R:
        status_code = status
        headers = {"Content-Type": content_type}
    return lambda *_a, **_kw: R()


def _write(path, slug, concept, resources=None):
    path.mkdir(parents=True, exist_ok=True)
    note = {"concept": concept, "status": "verified",
            "synthesis": f"about {concept}"}
    if resources is not None:
        note["resources"] = resources
    (path / f"{slug}.yaml").write_text(
        yaml.safe_dump(note, allow_unicode=True), encoding="utf-8")


def test_image_resource_gets_embed_kind_image(tmp_path):
    resources = [{"url": "https://x/plot.png", "title": "Plot",
                  "type": "visual", "why": "shows attention weights"}]
    _write(tmp_path / "_research_wiki", "x", NODE_ID, resources)

    bundle = build_bundle(FIXTURE, wiki_dir=tmp_path,
                          embed_head=_probe(200, "image/png"))

    embed = bundle["notes"][NODE_ID]["resources"][0]["embed"]
    assert embed == {"kind": "image", "src": "https://x/plot.png"}


def test_youtube_resource_gets_embed_kind_video_with_thumbnail():
    def boom(*_a, **_kw):
        raise AssertionError("a YouTube url must not be probed")

    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    resources = [{"url": url, "title": "Lecture",
                  "type": "lecture", "why": "walks through the derivation"}]

    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        _write(Path(tmp) / "_research_wiki", "x", NODE_ID, resources)
        bundle = build_bundle(FIXTURE, wiki_dir=tmp, embed_head=boom)

    embed = bundle["notes"][NODE_ID]["resources"][0]["embed"]
    assert embed == {"kind": "video",
                     "src": "https://img.youtube.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
                     "href": url}


def test_no_embed_probe_makes_every_resource_a_link_with_no_network_call(tmp_path):
    def boom(*_a, **_kw):
        raise AssertionError("embed_probe=False must never touch the network")

    resources = [
        {"url": "https://x/plot.png", "title": "Plot",
         "type": "visual", "why": "diagram"},
        {"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
         "title": "Lecture", "type": "lecture", "why": "walkthrough"},
    ]
    _write(tmp_path / "_research_wiki", "x", NODE_ID, resources)

    bundle = build_bundle(FIXTURE, wiki_dir=tmp_path,
                          embed_head=boom, embed_probe=False)

    embeds = [r["embed"] for r in bundle["notes"][NODE_ID]["resources"]]
    assert embeds == [{"kind": "link"}, {"kind": "link"}]


def test_note_with_no_resources_is_unchanged(tmp_path):
    _write(tmp_path / "_research_wiki", "x", NODE_ID, resources=None)

    bundle = build_bundle(FIXTURE, wiki_dir=tmp_path,
                          embed_head=lambda *_a, **_kw: (_ for _ in ()).throw(
                              AssertionError("no resources, nothing to probe")))

    note = bundle["notes"][NODE_ID]
    assert "resources" not in note
    assert note["synthesis"] == f"about {NODE_ID}"


def test_resource_keeps_existing_keys_and_gains_embed(tmp_path):
    resources = [{"url": "https://x/page.html", "title": "Explainer",
                  "type": "reference-impl", "why": "the canonical writeup"}]
    _write(tmp_path / "_research_wiki", "x", NODE_ID, resources)

    bundle = build_bundle(FIXTURE, wiki_dir=tmp_path,
                          embed_head=_probe(200, "text/html"))

    resource = bundle["notes"][NODE_ID]["resources"][0]
    assert resource["url"] == "https://x/page.html"
    assert resource["title"] == "Explainer"
    assert resource["type"] == "reference-impl"
    assert resource["why"] == "the canonical writeup"
    assert resource["embed"] == {"kind": "link"}


def test_same_url_across_notes_is_probed_once(tmp_path):
    calls = []

    def counting_head(url, *_a, **_kw):
        calls.append(url)
        class R:
            status_code = 200
            headers = {"Content-Type": "image/png"}
        return R()

    shared_url = "https://x/shared.png"
    resources = [{"url": shared_url, "title": "Plot",
                  "type": "visual", "why": "diagram"}]
    research_wiki = tmp_path / "_research_wiki"
    _write(research_wiki, "a", NODE_ID, resources)
    _write(research_wiki, "b", OTHER_NODE_ID, resources)

    bundle = build_bundle(FIXTURE, wiki_dir=tmp_path, embed_head=counting_head)

    assert calls == [shared_url]
    assert bundle["notes"][NODE_ID]["resources"][0]["embed"]["kind"] == "image"
    assert bundle["notes"][OTHER_NODE_ID]["resources"][0]["embed"]["kind"] == "image"


# --- og:image previews for `visual` explainers ------------------------------
# Every `visual` resource in the six built papers rendered as a bare link: the
# type means "visual explainer" (distill.pub, Jay Alammar), which is an HTML
# page, and only a direct image content-type was ever promoted. The preview
# GET is scoped to `visual` so a follow-up paper stays a plain link.

def _page(body):
    class R:
        status_code = 200
        headers = {"Content-Type": "text/html"}
        text = body
    return lambda *_a, **_kw: R()


def _head_by_suffix(*_a, **_kw):
    """embed_kind confirms an og:image really is an image before promoting it,
    so the head here has to tell a page from a picture."""
    url = _a[0] if _a else _kw.get("url", "")
    class R:
        status_code = 200
        headers = {"Content-Type":
                   "image/png" if url.endswith((".png", ".jpg", ".svg"))
                   else "text/html"}
    return R()


OG_PAGE = '<meta property="og:image" content="https://distill.pub/card.png">'


def test_a_visual_explainer_page_gets_its_og_image(tmp_path):
    resources = [{"url": "https://distill.pub/2016/deconv/", "title": "Deconv",
                  "type": "visual", "why": "animates the artifact"}]
    _write(tmp_path / "_research_wiki", "x", NODE_ID, resources)

    bundle = build_bundle(FIXTURE, wiki_dir=tmp_path,
                          embed_head=_head_by_suffix,
                          embed_get=_page(OG_PAGE))

    assert bundle["notes"][NODE_ID]["resources"][0]["embed"] == {
        "kind": "image", "src": "https://distill.pub/card.png"}


def test_a_non_visual_resource_is_never_fetched_for_a_preview(tmp_path):
    """A social card on every follow-up paper is noise, and it would cost a
    GET per resource across the whole build."""
    def boom(*_a, **_kw):
        raise AssertionError("only `visual` resources may be fetched")

    resources = [{"url": "https://arxiv.org/abs/1234.5678", "title": "Paper",
                  "type": "follow-up-paper", "why": "extends the result"}]
    _write(tmp_path / "_research_wiki", "x", NODE_ID, resources)

    bundle = build_bundle(FIXTURE, wiki_dir=tmp_path,
                          embed_head=_probe(200, "text/html"), embed_get=boom)

    assert bundle["notes"][NODE_ID]["resources"][0]["embed"] == {"kind": "link"}


def test_no_embed_probe_also_skips_the_preview_fetch(tmp_path):
    def boom(*_a, **_kw):
        raise AssertionError("embed_probe=False must never touch the network")

    resources = [{"url": "https://distill.pub/2016/deconv/", "title": "D",
                  "type": "visual", "why": "animation"}]
    _write(tmp_path / "_research_wiki", "x", NODE_ID, resources)

    bundle = build_bundle(FIXTURE, wiki_dir=tmp_path, embed_head=boom,
                          embed_get=boom, embed_probe=False)

    assert bundle["notes"][NODE_ID]["resources"][0]["embed"] == {"kind": "link"}


def test_the_same_url_cited_as_visual_and_as_paper_does_not_share_a_verdict(tmp_path):
    """The cache is keyed on url alone before this change, so whichever note
    was visited first would decide the other's embed."""
    calls = []

    def counting_get(url, *_a, **_kw):
        calls.append(url)
        return _page(OG_PAGE)()

    url = "https://distill.pub/2016/deconv/"
    _write(tmp_path / "_research_wiki", "a", NODE_ID,
           [{"url": url, "title": "D", "type": "follow-up-paper", "why": "w"}])
    _write(tmp_path / "_research_wiki", "b", OTHER_NODE_ID,
           [{"url": url, "title": "D", "type": "visual", "why": "w"}])

    bundle = build_bundle(FIXTURE, wiki_dir=tmp_path,
                          embed_head=_head_by_suffix,
                          embed_get=counting_get)

    assert bundle["notes"][NODE_ID]["resources"][0]["embed"] == {"kind": "link"}
    assert bundle["notes"][OTHER_NODE_ID]["resources"][0]["embed"]["kind"] == "image"
    assert len(calls) == 1, "the visual verdict is still cached, one GET only"
