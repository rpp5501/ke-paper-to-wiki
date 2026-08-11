"""Figures reach the reader, or the extraction was for nothing.

build_data inlines the whole bundle into src/data.gen.ts, so image bytes must
NOT go in it -- DDIM's assets are 12.8 MB, which as base64 would be ~17 MB of
JavaScript. They are copied where Vite serves static files and referenced by
url, so the browser fetches them lazily and the bundle stays a bundle.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from build_data import figure_urls, copy_figure_assets  # noqa: E402

PACK = {"figures": [
    {"id": "fig_1", "section": "sec_3", "caption": "The Transformer.",
     "graphics": ["Figures/ModalNet-21"], "assets": ["Figures/ModalNet-21.png"]},
    {"id": "fig_2", "section": "sec_3", "caption": "Two panels.",
     "graphics": ["a", "b"], "assets": ["vis/a.png", "vis/b.png"]},
    {"id": "fig_3", "section": "sec_8", "caption": "A TikZ drawing.",
     "graphics": [], "assets": []},
]}


def test_every_figure_with_an_image_gets_a_url():
    urls = figure_urls(PACK, base="figures/aiayn")

    assert urls["fig_1"]["images"] == ["figures/aiayn/Figures/ModalNet-21.png"]
    assert urls["fig_2"]["images"] == ["figures/aiayn/vis/a.png",
                                       "figures/aiayn/vis/b.png"]


def test_the_caption_travels_with_the_url():
    """A figure block in a page carries only an id; the caption the paper
    actually wrote lives in the pack."""
    urls = figure_urls(PACK, base="figures/aiayn")

    assert urls["fig_1"]["caption"] == "The Transformer."
    assert urls["fig_1"]["section"] == "sec_3"


def test_a_figure_with_no_image_still_appears_with_its_caption():
    """A TikZ figure has no file. The reader is told it exists rather than
    being shown a broken image."""
    urls = figure_urls(PACK, base="figures/aiayn")

    assert urls["fig_3"]["images"] == []
    assert urls["fig_3"]["caption"] == "A TikZ drawing."


def test_a_pack_with_no_figures_yields_nothing():
    assert figure_urls({}, base="figures/x") == {}


def test_the_images_are_copied_where_vite_serves_them(tmp_path):
    src = tmp_path / "assets"
    (src / "Figures").mkdir(parents=True)
    (src / "Figures" / "ModalNet-21.png").write_bytes(b"\x89PNG-one")
    (src / "vis").mkdir()
    (src / "vis" / "a.png").write_bytes(b"\x89PNG-two")
    (src / "vis" / "b.png").write_bytes(b"\x89PNG-three")
    public = tmp_path / "public"

    copied = copy_figure_assets(PACK, src, public, base="figures/aiayn")

    assert copied == 3
    assert (public / "figures" / "aiayn" / "Figures"
            / "ModalNet-21.png").read_bytes() == b"\x89PNG-one"
    assert (public / "figures" / "aiayn" / "vis" / "b.png").exists()


def test_an_asset_missing_from_disk_is_skipped_not_faked(tmp_path):
    """The pack names what it resolved at P1; if the file is not there now,
    copying nothing is right and the url would 404 -- better than writing an
    empty file that renders as a broken image."""
    src = tmp_path / "assets"
    src.mkdir()
    public = tmp_path / "public"

    assert copy_figure_assets(PACK, src, public, base="figures/aiayn") == 0


def test_no_assets_dir_copies_nothing(tmp_path):
    assert copy_figure_assets(PACK, None, tmp_path, base="figures/x") == 0
