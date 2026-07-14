import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build_data import (build_bundle, main, reading_path, strip_images,
                        to_data_ts)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = ROOT / "fixtures" / "aiayn_concept_graph.json"
COMMITTED_DATA = ROOT / "dashboard" / "src" / "data.gen.ts"
TINY_PACK_PATH = ROOT / "fixtures" / "aiayn_tiny_pack.json"
PAGES_DIR = ROOT / "fixtures" / "pages"
WIKI_DIR = ROOT / "fixtures" / "wiki"
FIXTURE = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
PACK = {"meta": {"source": "arXiv:1706.03762", "title": "AIAYN",
                 "generated": "2026-07-09"},
        "extraction": {"path": "latex", "equation_fidelity": "exact"},
        "sections": [{"id": "sec_3_2", "title": "SDPA", "level": 2, "text": "t"}],
        "equations": [{"id": "eq_1", "latex": "x", "section": "sec_3_2"}],
        "references": [], "figures": []}


def test_bundle_has_all_contract_keys():
    b = build_bundle(FIXTURE, pack=PACK)
    for k in ("meta", "nodes", "edges", "pages", "notes", "hotspots",
              "clusters", "tour", "provenance", "centrality", "eqIndex",
              "trace", "glossary"):
        assert k in b, k


def test_dependent_side_matches_edge_direction_contract():
    assert build_bundle(FIXTURE, pack=PACK)["dependentSide"] == {
        "part-of": "dst",
        "prerequisite": "dst",
        "builds-on": "src",
    }


def test_tour_is_deterministic_reading_path_head():
    b = build_bundle(FIXTURE, pack=PACK)
    order = reading_path(FIXTURE)
    assert [s["nodeIds"][0] for s in b["tour"]] == order[:5]
    assert all(s["title"] and s["description"] for s in b["tour"])


def test_clusters_fall_back_to_level1_grouping():
    b = build_bundle(FIXTURE, pack=PACK)
    ids = {c["id"] for c in b["clusters"]}
    assert "attention" in ids
    members = next(c for c in b["clusters"] if c["id"] == "attention")["nodeIds"]
    assert "scaled-dot-product-attention" in members


def test_centrality_present_for_every_node():
    b = build_bundle(FIXTURE, pack=PACK)
    assert set(b["centrality"]) == {n["id"] for n in FIXTURE["nodes"]}


def test_eq_index_maps_equation_to_anchored_concepts():
    g = json.loads(json.dumps(FIXTURE))
    g["nodes"][0]["source_ref"] = "sec_3_2"
    b = build_bundle(g, pack=PACK)
    assert g["nodes"][0]["id"] in b["eqIndex"]["eq_1"]


def test_eq_index_normalizes_dotted_pack_sections_to_graph_source_refs():
    graph = {
        "meta": {"kind": "concept", "generated": "2026-07-09"},
        "nodes": [{
            "id": "scaled-dot-product-attention",
            "kind": "concept",
            "label": "Scaled dot-product attention",
            "source_ref": "sec:3.2.1",
        }],
        "edges": [],
    }
    pack = {
        "meta": {"source": "paper", "title": "Attention",
                 "generated": "2026-07-09"},
        "extraction": {"path": "latex", "equation_fidelity": "exact"},
        "sections": [{"id": "sec_3_2_1", "title": "Attention Function",
                      "level": 3, "text": "scaled attention"}],
        "equations": [{"id": "eq_attention", "latex": r"1/\sqrt{d_k}",
                       "section": "sec_3_2_1"}],
        "references": [],
        "figures": [],
    }

    bundle = build_bundle(graph, pack=pack)

    assert bundle["eqIndex"]["eq_attention"] == [
        "scaled-dot-product-attention"
    ]


def test_eq_index_does_not_join_blank_sections_or_node_refs():
    graph = {
        "meta": {"kind": "concept", "generated": "2026-07-09"},
        "nodes": [
            {"id": "missing-ref", "kind": "concept", "label": "Missing"},
            {"id": "blank-ref", "kind": "concept", "label": "Blank",
             "source_ref": "  "},
        ],
        "edges": [],
    }
    pack = {
        "meta": {"source": "paper", "title": "Attention",
                 "generated": "2026-07-09"},
        "extraction": {},
        "sections": [],
        "equations": [
            {"id": "missing-section", "latex": "x"},
            {"id": "blank-section", "latex": "y", "section": "  "},
        ],
        "references": [],
        "figures": [],
    }

    bundle = build_bundle(graph, pack=pack)

    assert bundle["eqIndex"] == {
        "blank-section": [],
        "missing-section": [],
    }


def test_repo_fixture_bundle_exercises_explain_drawer_contract():
    pack = json.loads(TINY_PACK_PATH.read_text(encoding="utf-8"))

    bundle = build_bundle(
        FIXTURE, pack=pack, pages_dir=PAGES_DIR, wiki_dir=WIKI_DIR)

    concept = "scaled-dot-product-attention"
    assert "sdpa" in bundle["pages"]
    assert all(anchor in bundle["pages"]["sdpa"] for anchor in (
        "{#tldr}", "{#intuition}", "{#mechanics}",
        "{#the-math}", "{#go-deeper}",
    ))
    assert r"\sqrt{d_k}" in bundle["pages"]["sdpa"]
    assert bundle["notes"][concept]["synthesis"]
    assert bundle["glossary"][concept]["softmax"]
    assert concept in bundle["eqIndex"]["eq_1"]
    written = [item for item in bundle["trace"]
               if item["phase"] == "written"]
    assert [item["nodeId"] for item in written] == [concept]
    node_ids = {node["id"] for node in bundle["nodes"]}
    assert {item["nodeId"] for item in bundle["trace"]} <= node_ids


def test_strip_images_removes_and_counts():
    md = "before ![diagram](../assets/x.png) after"
    out, n = strip_images(md)
    assert "![" not in out and "x.png" not in out and n == 1


def test_note_trace_dates_are_content_based_and_mtime_stable(tmp_path):
    pages_dir = tmp_path / "pages"
    wiki_dir = tmp_path / "wiki"
    pages_dir.mkdir()
    wiki_dir.mkdir()
    (pages_dir / "01_attention.md").write_text(
        "before ![diagram](../assets/x.png) after", encoding="utf-8")
    notes = {
        "attention.yaml": (
            'concept: attention\nstatus: verified\ndate: "2024-01-02"\n'
            'generated: "2024-01-01"\nsynthesis: dated\n'),
        "encoder-decoder-stack.yaml": (
            'concept: encoder-decoder-stack\nstatus: verified\n'
            'generated: "2024-02-03"\nsynthesis: generated\n'),
        "positional-encoding.yaml": (
            'concept: positional-encoding\nstatus: verified\n'
            'synthesis: fallback\n'),
    }
    for name, content in notes.items():
        path = wiki_dir / name
        path.write_text(content, encoding="utf-8")
        os.utime(path, (946684800, 946684800))

    first = build_bundle(FIXTURE, pages_dir=pages_dir, wiki_dir=wiki_dir)
    for path in wiki_dir.glob("*.yaml"):
        os.utime(path, (1893456000, 1893456000))
    second = build_bundle(FIXTURE, pages_dir=pages_dir, wiki_dir=wiki_dir)

    assert first == second
    researched_dates = {
        item["nodeId"]: item["date"]
        for item in first["trace"] if item["phase"] == "researched"
    }
    assert researched_dates == {
        "attention": "2024-01-02",
        "encoder-decoder-stack": "2024-02-03",
        "positional-encoding": FIXTURE["meta"]["generated"],
    }
    assert {node_id: note["date"] for node_id, note in first["notes"].items()} == {
        "attention": "2024-01-02",
        "encoder-decoder-stack": "2024-02-03",
        "positional-encoding": FIXTURE["meta"]["generated"],
    }
    assert first["pages"]["attention"] == "before  after"
    assert {item["date"] for item in first["trace"]
            if item["phase"] == "written"} == {FIXTURE["meta"]["generated"]}


def test_repo_dir_source_dates_prefer_git_and_use_generated_fallback(tmp_path):
    repo = tmp_path / "repo"
    source_dir = repo / "src"
    source_dir.mkdir(parents=True)
    tracked = source_dir / "tracked.py"
    untracked = source_dir / "untracked.py"
    tracked.write_text("def tracked(): pass\n", encoding="utf-8")
    untracked.write_text("def untracked(): pass\n", encoding="utf-8")

    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "add", "src/tracked.py"], cwd=repo, check=True)
    commit_env = os.environ | {
        "GIT_AUTHOR_DATE": "2024-01-02T12:00:00+00:00",
        "GIT_COMMITTER_DATE": "2024-01-02T12:00:00+00:00",
    }
    subprocess.run(
        ["git", "-c", "user.name=Dashboard Tests",
         "-c", "user.email=dashboard@example.invalid",
         "commit", "-q", "-m", "fixture"],
        cwd=repo, env=commit_env, check=True,
    )

    graph = {
        "meta": {"kind": "code", "generated": "2026-07-09"},
        "nodes": [
            {"id": "tracked", "kind": "function", "label": "tracked",
             "source_ref": "src/tracked.py:L1"},
            {"id": "untracked", "kind": "function", "label": "untracked",
             "source_ref": "src/untracked.py:L1"},
            {"id": "missing-ref", "kind": "class", "label": "missing-ref"},
            {"id": "empty-ref", "kind": "file", "label": "empty-ref",
             "source_ref": ""},
            {"id": "missing-file", "kind": "route", "label": "missing-file",
             "source_ref": "src/missing.py:L1"},
            {"id": "concept", "kind": "concept", "label": "concept"},
        ],
        "edges": [],
    }

    os.utime(tracked, (946684800, 946684800))
    os.utime(untracked, (946684800, 946684800))
    first = build_bundle(graph, repo_dir=repo)
    os.utime(tracked, (1893456000, 1893456000))
    os.utime(untracked, (1893456000, 1893456000))
    second = build_bundle(graph, repo_dir=repo)

    assert first["mtimes"] == {
        "tracked": "2024-01-02",
        "untracked": graph["meta"]["generated"],
        "missing-ref": graph["meta"]["generated"],
        "empty-ref": graph["meta"]["generated"],
        "missing-file": graph["meta"]["generated"],
    }
    assert second["mtimes"] == first["mtimes"]


def test_repo_dir_source_dates_fall_back_when_git_is_unavailable(tmp_path):
    repo = tmp_path / "not-a-git-repo"
    repo.mkdir()
    (repo / "module.py").write_text("value = 1\n", encoding="utf-8")
    graph = {
        "meta": {"kind": "code", "generated": "2026-07-09"},
        "nodes": [
            {"id": "module", "kind": "function", "label": "module",
             "source_ref": "module.py:L1"},
        ],
        "edges": [],
    }

    assert build_bundle(graph, repo_dir=repo)["mtimes"] == {
        "module": graph["meta"]["generated"],
    }


def test_bundle_without_repo_dir_omits_mtimes():
    assert "mtimes" not in build_bundle(FIXTURE, pack=PACK)


def test_ts_output_is_wellformed_and_unicode_raw():
    b = build_bundle(FIXTURE, pack=PACK)
    ts = to_data_ts(b)
    assert ts.startswith("// generated by build_data.py")
    assert "export const KE_DATA" in ts
    assert "√dₖ" in ts
    json.loads(ts.split("=", 1)[1].rstrip().rstrip(";"))


def test_cli_writes_utf8_with_byte_stable_lf(tmp_path):
    out = tmp_path / "data.gen.ts"

    assert main(["--graph", str(FIXTURE_PATH), "--out", str(out)]) == 0

    data = out.read_bytes()
    assert data.startswith(b"// generated by build_data.py")
    assert b"\r\n" not in data
    assert data.endswith(b";\n")
    assert "√dₖ".encode() in data


def test_repo_fixture_regeneration_matches_committed_data(tmp_path):
    out = tmp_path / "data.gen.ts"

    assert main([
        "--graph", str(FIXTURE_PATH),
        "--pack", str(TINY_PACK_PATH),
        "--pages-dir", str(PAGES_DIR),
        "--wiki-dir", str(WIKI_DIR),
        "--out", str(out),
    ]) == 0

    assert (out.read_text(encoding="utf-8") ==
            COMMITTED_DATA.read_text(encoding="utf-8"))
