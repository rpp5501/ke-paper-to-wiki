"""R15.11 — section_key module-level helper + build_bundle --pack sections."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build_data import build_bundle, section_key, to_data_ts

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = json.loads(
    (ROOT / "fixtures" / "aiayn_concept_graph.json").read_text(encoding="utf-8"))


def test_section_key_vectors():
    assert section_key("sec_3_2") == "3.2"
    assert section_key("sec:3.2") == "3.2"
    assert section_key("§3.2") == "3.2"
    assert section_key("Sec 3.2.1") == "3.2.1"
    assert section_key("") == ""
    assert section_key(None) == ""


def test_pack_emits_sections():
    pack = {"sections": [{"id": "sec_3_2", "title": "SDPA", "level": 2,
                          "text": "t"}],
            "extraction": {}, "equations": []}
    bundle = build_bundle(FIXTURE, pack=pack)
    assert bundle["sections"]["3.2"] == {"title": "SDPA", "text": "t"}


def test_no_pack_leaves_bundle_untouched():
    bundle = build_bundle(FIXTURE)
    assert "sections" not in bundle
    assert '"sections"' not in to_data_ts(bundle)
