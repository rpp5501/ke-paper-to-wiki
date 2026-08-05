"""A paper-wide glossary, so shared terminology is defined once.

The hover mechanism was already built end to end (mathHtml tokenizes prose and
marks terms; ArticleView and Drawer both pass GLOSSARY[nodeId]) but keyed per
concept, so a term used across twenty pages had to be repeated in twenty notes.
Terms like "d-separation", "Markov" or "idempotence" belong to the paper, not
to one of its concepts.
"""
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build_data import build_bundle

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = json.loads(
    (ROOT / "fixtures" / "aiayn_concept_graph.json").read_text(encoding="utf-8"))
NODE_ID = FIXTURE["nodes"][0]["id"]


def _wiki(tmp_path, notes):
    for name, note in notes.items():
        (tmp_path / f"{name}.yaml").write_text(
            yaml.safe_dump(note, allow_unicode=True), encoding="utf-8")
    return tmp_path


def test_paper_glossary_applies_to_every_concept(tmp_path):
    _wiki(tmp_path, {"_paper": {"concept": "_paper", "status": "verified",
                                "synthesis": "",
                                "glossary": {"d-separation": "A graphical criterion."}}})

    bundle = build_bundle(FIXTURE, wiki_dir=tmp_path)

    for node in FIXTURE["nodes"]:
        assert bundle["glossary"][node["id"]]["d-separation"] == "A graphical criterion."


def test_a_concept_entry_overrides_the_paper_one(tmp_path):
    """The concept that owns a term may define it more precisely."""
    _wiki(tmp_path, {
        "_paper": {"concept": "_paper", "status": "verified", "synthesis": "",
                   "glossary": {"Markov": "General sense."}},
        "specific": {"concept": NODE_ID, "status": "verified", "synthesis": "",
                     "glossary": {"Markov": "Sense used on this page."}}})

    bundle = build_bundle(FIXTURE, wiki_dir=tmp_path)

    assert bundle["glossary"][NODE_ID]["Markov"] == "Sense used on this page."


def test_the_paper_note_is_not_itself_a_concept(tmp_path):
    """_paper carries terminology, not research: it must not appear as a note
    or as a trace row for a node that does not exist."""
    _wiki(tmp_path, {"_paper": {"concept": "_paper", "status": "verified",
                                "synthesis": "", "glossary": {"x": "y"}}})

    bundle = build_bundle(FIXTURE, wiki_dir=tmp_path)

    assert "_paper" not in bundle["notes"]
    assert not [t for t in bundle["trace"] if t["nodeId"] == "_paper"]


def test_no_paper_note_leaves_per_concept_behaviour_alone(tmp_path):
    _wiki(tmp_path, {"n": {"concept": NODE_ID, "status": "verified",
                           "synthesis": "", "glossary": {"Q": "Query."}}})

    bundle = build_bundle(FIXTURE, wiki_dir=tmp_path)

    assert bundle["glossary"] == {NODE_ID: {"Q": "Query."}}
