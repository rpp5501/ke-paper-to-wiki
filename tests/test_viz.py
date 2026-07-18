"""R13 slice 1 — template instantiation, manifest contract, gate_viz."""
import json
from pathlib import Path

import pytest

from paper_skill.viz import (
    MAX_VIZ_BYTES,
    PLACEHOLDER,
    TEMPLATES_DIR,
    escape_params_json,
    gate_viz_dir,
    instantiate_template,
    load_manifest,
    page_sha256,
    write_viz,
)

TEMPLATE_IDS = [
    "attention-heatmap",
    "softmax-temperature",
    "positional-encoding",
    "gradient-descent-2d",
    "vector-projection",
]


@pytest.fixture
def page(tmp_path):
    p = tmp_path / "04_sdpa.md"
    p.write_text("# SDPA\n\n## The Math {#the-math}\n", encoding="utf-8")
    return p


def _write_one(tmp_path, page, **overrides):
    kwargs = dict(
        title="t", caption="c", prompt="bet?", page_path=page, generated="2026-07-17"
    )
    kwargs.update(overrides)
    return write_viz(
        tmp_path / "viz", "sdpa", "attention-heatmap",
        {"tokens": ["a", "b"], "prompt": "bet?"}, **kwargs
    )


# --- templates -------------------------------------------------------------

@pytest.mark.parametrize("tid", TEMPLATE_IDS)
def test_template_exists_and_has_placeholder(tid):
    tpl = (TEMPLATES_DIR / f"{tid.replace('-', '_')}.html").read_text(encoding="utf-8")
    assert PLACEHOLDER in tpl
    assert "<math" in tpl, "design rule: MathML equation required"
    assert "<link" not in tpl.lower(), "design rule: fully offline"
    assert "fetch(" not in tpl


@pytest.mark.parametrize("tid", TEMPLATE_IDS)
def test_template_under_size_cap(tid):
    html = instantiate_template(tid, {"tokens": ["a", "b", "c"], "prompt": "x"})
    assert len(html.encode("utf-8")) <= MAX_VIZ_BYTES


def test_instantiate_replaces_placeholder():
    html = instantiate_template("attention-heatmap", {"seed": 7})
    assert PLACEHOLDER not in html
    assert '"seed": 7' in html


def test_softmax_rows_are_added_to_their_actual_parent():
    html = instantiate_template("softmax-temperature", {"labels": ["a", "b"]})
    assert "logitsDiv.appendChild(row)" in html
    assert 'insertBefore(row, document.getElementById("tempRow"))' not in html


def test_unknown_template_raises():
    with pytest.raises(FileNotFoundError):
        instantiate_template("no-such-template", {})


# --- injection guard --------------------------------------------------------

def test_escape_params_json_neutralizes_script_close():
    payload = json.dumps({"prompt": "</script><script>alert(1)</script>"})
    escaped = escape_params_json(payload)
    assert "</" not in escaped
    assert json.loads(escaped.replace("<\\/", "</")) is not None


def test_hostile_params_pass_gate(tmp_path, page):
    write_viz(
        tmp_path / "viz", "sdpa", "attention-heatmap",
        {"prompt": "</script><script>alert(1)</script>"},
        title="t", caption="c", prompt="bet?", page_path=page,
    )
    assert gate_viz_dir(tmp_path / "viz") == []


# --- manifest contract ------------------------------------------------------

def test_write_viz_manifest_entry(tmp_path, page):
    entry = _write_one(tmp_path, page)
    assert entry["kind"] == "template"
    assert entry["template_id"] == "attention-heatmap"
    assert entry["prompt"] == "bet?"
    assert entry["page"] == "04_sdpa.md"
    assert entry["page_sha256"] == page_sha256(page)
    manifest = load_manifest(tmp_path / "viz")
    assert manifest["sdpa"] == entry
    assert (tmp_path / "viz" / entry["src"]).exists()


def test_write_viz_merges_manifest(tmp_path, page):
    _write_one(tmp_path, page)
    write_viz(
        tmp_path / "viz", "attention", "softmax-temperature", {"labels": ["a"]},
        title="t2", caption="c2", prompt="p2", page_path=page,
    )
    manifest = load_manifest(tmp_path / "viz")
    assert set(manifest) == {"sdpa", "attention"}


# --- gate -------------------------------------------------------------------

def test_gate_passes_on_valid_output(tmp_path, page):
    _write_one(tmp_path, page)
    assert gate_viz_dir(tmp_path / "viz") == []


def test_gate_missing_manifest(tmp_path):
    assert gate_viz_dir(tmp_path) == [f"missing manifest.json in {tmp_path}"]


def test_gate_flags_missing_prompt(tmp_path, page):
    _write_one(tmp_path, page, prompt="")
    findings = gate_viz_dir(tmp_path / "viz")
    assert any("missing field 'prompt'" in f for f in findings)


def test_gate_flags_network_ref(tmp_path, page):
    _write_one(tmp_path, page)
    f = tmp_path / "viz" / "sdpa.html"
    f.write_text(
        f.read_text(encoding="utf-8").replace(
            "</body>", '<img src="https://evil.example/x.png"></body>'
        ),
        encoding="utf-8",
    )
    findings = gate_viz_dir(tmp_path / "viz")
    assert any("external src=" in x for x in findings)


def test_gate_allows_xmlns_namespace(tmp_path, page):
    _write_one(tmp_path, page)
    html = (tmp_path / "viz" / "sdpa.html").read_text(encoding="utf-8")
    assert 'xmlns="http://www.w3.org/1998/Math/MathML"' in html
    assert gate_viz_dir(tmp_path / "viz") == []


def test_gate_flags_oversize(tmp_path, page):
    _write_one(tmp_path, page)
    f = tmp_path / "viz" / "sdpa.html"
    f.write_text(
        f.read_text(encoding="utf-8") + "<!--" + "x" * MAX_VIZ_BYTES + "-->",
        encoding="utf-8",
    )
    findings = gate_viz_dir(tmp_path / "viz")
    assert any("cap" in x for x in findings)


def test_gate_flags_leftover_placeholder(tmp_path, page):
    _write_one(tmp_path, page)
    f = tmp_path / "viz" / "sdpa.html"
    f.write_text(
        f.read_text(encoding="utf-8") + f"<!-- {PLACEHOLDER} -->", encoding="utf-8"
    )
    findings = gate_viz_dir(tmp_path / "viz")
    assert any("un-instantiated" in x for x in findings)


def test_gate_flags_missing_src_file(tmp_path, page):
    _write_one(tmp_path, page)
    (tmp_path / "viz" / "sdpa.html").unlink()
    findings = gate_viz_dir(tmp_path / "viz")
    assert any("does not exist" in x for x in findings)


# --- CLI: propose + build ----------------------------------------------------

from paper_skill.viz import build_pack, main, propose, suggest_template  # noqa: E402

FIXTURE_ROOT = Path(__file__).resolve().parent.parent / "fixtures"


def test_suggest_template_matches_attention():
    node = {"id": "scaled-dot-product-attention", "label": "SDPA"}
    assert suggest_template(node, "") == "attention-heatmap"


def test_suggest_template_none_for_unknown():
    assert suggest_template({"id": "residual", "label": "Residual"}, "") is None


def test_propose_requires_math_tier_on_disk():
    graph = json.loads(
        (FIXTURE_ROOT / "aiayn_concept_graph.json").read_text(encoding="utf-8"))
    ids = [c["id"] for c in propose(graph, FIXTURE_ROOT / "pages")]
    # only 04_sdpa.md exists with a The Math tier in the fixture
    assert ids == ["scaled-dot-product-attention"]


def test_propose_caps_at_k(tmp_path):
    pages = tmp_path / "pages"
    pages.mkdir()
    nodes, edges = [], []
    for i in range(6):
        (pages / f"{i}.md").write_text("## The Math {#the-math}\nx",
                                       encoding="utf-8")
        nodes.append({"id": f"n{i}", "label": f"N{i}", "level": 1,
                      "page": f"{i}.md"})
        if i:
            edges.append({"src": "n0", "dst": f"n{i}", "kind": "part-of"})
    got = propose({"nodes": nodes, "edges": edges}, pages, k=4)
    assert len(got) == 4
    assert got[0]["id"] == "n0"  # highest degree first


def test_build_pack_end_to_end(tmp_path, page):
    params = {
        "sdpa": {
            "template_id": "attention-heatmap",
            "title": "t", "caption": "c", "prompt": "bet?",
            "page": page.name,
            "params": {"tokens": ["a", "b"]},
        }
    }
    findings = build_pack(params, page.parent, tmp_path / "viz")
    assert findings == []
    assert (tmp_path / "viz" / "sdpa.html").exists()


def test_cli_build_fails_on_unknown_template(tmp_path, page):
    pfile = tmp_path / "p.json"
    pfile.write_text(json.dumps({
        "x": {"template_id": "no-such", "page": page.name,
              "title": "t", "caption": "c", "prompt": "p"},
    }), encoding="utf-8")
    rc = main(["build", "--params", str(pfile),
               "--pages-dir", str(page.parent),
               "--out", str(tmp_path / "viz")])
    assert rc == 1


def test_cli_propose_runs(capsys):
    rc = main(["propose", str(FIXTURE_ROOT / "aiayn_concept_graph.json"),
               "--pages-dir", str(FIXTURE_ROOT / "pages")])
    assert rc == 0
    out = capsys.readouterr().out
    assert "PROPOSAL ONLY" in out
    assert "scaled-dot-product-attention" in out


# --- staleness hook ----------------------------------------------------------

def test_page_hash_changes_on_page_edit(tmp_path, page):
    entry = _write_one(tmp_path, page)
    page.write_text("# SDPA v2\n", encoding="utf-8")
    assert page_sha256(page) != entry["page_sha256"]
