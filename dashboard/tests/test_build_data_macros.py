"""The paper's own \\newcommand table has to reach KaTeX.

latex_pack copies equations VERBATIM (equation_fidelity "exact"), so a paper's
private notation travels with them. If the macro table stops at the pack, KaTeX
throws on the first unknown control sequence and renderMathToString falls back
to printing raw LaTeX: the reader sees "\\doo" where the paper means "do".
All 11 equations of arXiv:1306.1043 were affected.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build_data import build_bundle, to_data_ts

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = json.loads(
    (ROOT / "fixtures" / "aiayn_concept_graph.json").read_text(encoding="utf-8"))

PACK = {"sections": [{"id": "sec_1", "title": "S", "level": 1, "text": "t"}],
        "extraction": {}, "equations": [],
        "macros": {"\\G": "\\mathcal{G}", "\\doo": "\\operatorname{do}"}}


def test_pack_macros_reach_the_bundle():
    assert build_bundle(FIXTURE, pack=PACK)["macros"] == PACK["macros"]


def test_pack_without_macros_emits_an_empty_table():
    """An older pack predates the field; consumers still want a table to spread."""
    pack = {k: v for k, v in PACK.items() if k != "macros"}
    assert build_bundle(FIXTURE, pack=pack)["macros"] == {}


def test_no_pack_leaves_the_bundle_untouched():
    """Opt-in discipline: without --pack the key is absent, byte for byte."""
    bundle = build_bundle(FIXTURE)
    assert "macros" not in bundle
    assert '"macros"' not in to_data_ts(bundle)
