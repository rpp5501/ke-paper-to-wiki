import yaml
from paper_skill.toc import write_toc, load_approved_toc

ROWS = [{"id": "transformer", "label": "The Transformer", "level": 0,
         "include": True, "research": True,
         "definition": "d", "sub_questions": ["q"]}]


def test_written_toc_defaults_unapproved(tmp_path):
    p = tmp_path / "concept_toc.yaml"
    write_toc(ROWS, p)
    doc = yaml.safe_load(p.read_text(encoding="utf-8"))
    assert doc["approved"] is False
    assert load_approved_toc(p)["status"] == "not_approved"


def test_approved_toc_loads_included_rows(tmp_path):
    p = tmp_path / "concept_toc.yaml"
    write_toc(ROWS + [{**ROWS[0], "id": "skip-me", "include": False}], p)
    doc = yaml.safe_load(p.read_text(encoding="utf-8"))
    doc["approved"] = True
    p.write_text(yaml.safe_dump(doc, allow_unicode=True), encoding="utf-8")
    r = load_approved_toc(p)
    assert r["status"] == "ok"
    assert [row["id"] for row in r["rows"]] == ["transformer"]
