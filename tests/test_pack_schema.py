import json
from pathlib import Path
import jsonschema

SCHEMA = json.loads((Path(__file__).resolve().parents[1] / "src" / "paper_skill" /
                     "schemas" / "paper_pack.schema.json").read_text(encoding="utf-8"))

MINIMAL = {"meta": {"source": "arXiv:1706.03762", "title": "t", "generated": "2026-07-09"},
           "extraction": {"path": "latex", "equation_fidelity": "exact"},
           "sections": [], "equations": [], "references": [], "figures": []}


def test_minimal_pack_validates():
    jsonschema.validate(MINIMAL, SCHEMA)


def test_extraction_block_is_mandatory():
    import pytest
    bad = {k: v for k, v in MINIMAL.items() if k != "extraction"}
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, SCHEMA)
