"""_load_notes must find notes under wiki_dir/_research_wiki/, which is where
research_mcp.wiki.wiki_put actually writes them (see wiki.py: _wiki_dir).
Globbing wiki_dir itself only matched a legacy flat layout, so every note the
live pipeline ever produced was invisible to the dashboard.
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


def _write(path, slug, concept):
    path.mkdir(parents=True, exist_ok=True)
    (path / f"{slug}.yaml").write_text(
        yaml.safe_dump({"concept": concept, "status": "verified",
                        "synthesis": f"about {concept}"}, allow_unicode=True),
        encoding="utf-8")


def test_note_under_research_wiki_subdir_reaches_the_bundle(tmp_path):
    _write(tmp_path / "_research_wiki", "x", NODE_ID)

    bundle = build_bundle(FIXTURE, wiki_dir=tmp_path)

    assert bundle["notes"][NODE_ID]["synthesis"] == f"about {NODE_ID}"


def test_note_directly_in_wiki_dir_still_reaches_the_bundle(tmp_path):
    """Older artifacts wrote flat into wiki_dir; keep reading those too."""
    _write(tmp_path, "x", NODE_ID)

    bundle = build_bundle(FIXTURE, wiki_dir=tmp_path)

    assert bundle["notes"][NODE_ID]["synthesis"] == f"about {NODE_ID}"


def test_same_slug_in_both_places_is_loaded_once_preferring_research_wiki(tmp_path):
    _write(tmp_path, "x", NODE_ID)
    (tmp_path / "_research_wiki").mkdir(parents=True, exist_ok=True)
    (tmp_path / "_research_wiki" / "x.yaml").write_text(
        yaml.safe_dump({"concept": NODE_ID, "status": "verified",
                        "synthesis": "live copy"}, allow_unicode=True),
        encoding="utf-8")

    bundle = build_bundle(FIXTURE, wiki_dir=tmp_path)

    assert len(bundle["notes"]) == 1
    assert bundle["notes"][NODE_ID]["synthesis"] == "live copy"
    # Verify dedup is real: if both files were loaded without deduping, this would
    # have two trace rows for the same node. This assertion proves the implementation
    # actually suppressed the duplicate, not just happened to overwrite by dict key.
    assert len([t for t in bundle["trace"] if t["nodeId"] == NODE_ID]) == 1


def test_missing_wiki_dir_still_returns_empty(tmp_path):
    bundle = build_bundle(FIXTURE, wiki_dir=tmp_path / "does-not-exist")

    assert bundle["notes"] == {}
    assert bundle["glossary"] == {}


def test_empty_wiki_dir_still_returns_empty(tmp_path):
    bundle = build_bundle(FIXTURE, wiki_dir=tmp_path)

    assert bundle["notes"] == {}
    assert bundle["glossary"] == {}
