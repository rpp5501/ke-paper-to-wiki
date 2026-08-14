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
