"""R13 slice 2 — build_data --viz-dir: opt-in emission + staleness."""
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build_data import build_bundle, to_data_ts

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = json.loads(
    (ROOT / "fixtures" / "aiayn_concept_graph.json").read_text(encoding="utf-8"))
PAGES_DIR = ROOT / "fixtures" / "pages"
VIZ_DIR = ROOT / "fixtures" / "viz"


def test_no_viz_dir_leaves_bundle_untouched():
    bundle = build_bundle(FIXTURE, pages_dir=str(PAGES_DIR))
    assert "viz" not in bundle
    assert '"viz"' not in to_data_ts(bundle)


def test_viz_dir_emits_entries_with_srcdoc():
    bundle = build_bundle(FIXTURE, pages_dir=str(PAGES_DIR),
                          viz_dir=str(VIZ_DIR))
    viz = bundle["viz"]
    assert set(viz) == {"scaled-dot-product-attention", "attention"}
    entry = viz["scaled-dot-product-attention"]
    assert entry["kind"] == "template"
    assert entry["templateId"] == "attention-heatmap"
    assert entry["prompt"]
    assert entry["caption"]
    assert "<script" in entry["srcdoc"]
    assert "{{PARAMS_JSON}}" not in entry["srcdoc"]


def test_fresh_pages_are_not_stale():
    bundle = build_bundle(FIXTURE, pages_dir=str(PAGES_DIR),
                          viz_dir=str(VIZ_DIR))
    assert all(not e["stale"] for e in bundle["viz"].values())


def test_edited_page_flips_stale(tmp_path):
    pages = tmp_path / "pages"
    shutil.copytree(PAGES_DIR, pages)
    sdpa = pages / "04_sdpa.md"
    sdpa.write_text(sdpa.read_text(encoding="utf-8") + "\nedited\n",
                    encoding="utf-8")
    bundle = build_bundle(FIXTURE, pages_dir=str(pages), viz_dir=str(VIZ_DIR))
    assert all(e["stale"] for e in bundle["viz"].values())


def test_missing_manifest_is_empty_not_fatal(tmp_path):
    bundle = build_bundle(FIXTURE, pages_dir=str(PAGES_DIR),
                          viz_dir=str(tmp_path))
    assert bundle["viz"] == {}
