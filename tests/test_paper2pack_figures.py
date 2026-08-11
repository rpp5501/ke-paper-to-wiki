"""The images are inside the e-print tarball we already download.

AIAYN ships 12 of them, MM-BD 45. A figure record naming Figures/ModalNet-21
is only useful if the bytes of Figures/ModalNet-21.png come with it -- a
caption without its picture is a promise the reader cannot cash.
"""
import io
import tarfile

from paper_skill.paper2pack import _pack_from_tarball, extract_assets

PAPER = r"""\documentclass{article}
\title{Attention Is All You Need}
\begin{document}
\section{Model Architecture}
The encoder maps a sequence to representations.
\begin{figure}
\includegraphics[scale=0.6]{Figures/ModalNet-21}
\caption{The Transformer - model architecture.}
\end{figure}
\end{document}"""

PNG = b"\x89PNG\r\n\x1a\n" + b"fake image bytes"


def _tarball(members: dict) -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as tf:
        for name, data in members.items():
            if isinstance(data, str):
                data = data.encode("utf-8")
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))
    return buf.getvalue()


TARBALL = _tarball({"main.tex": PAPER, "Figures/ModalNet-21.png": PNG})


def test_the_graphic_reference_resolves_to_the_file_that_holds_it():
    """LaTeX omits the extension: \\includegraphics{Figures/ModalNet-21} is
    satisfied by ModalNet-21.png, .pdf or .jpg, whichever the tarball ships."""
    assets = extract_assets(TARBALL, [{"id": "fig_1",
                                       "graphics": ["Figures/ModalNet-21"]}])

    assert assets == {"Figures/ModalNet-21.png": PNG}


def test_a_graphic_with_no_file_behind_it_is_skipped_not_faked():
    assets = extract_assets(TARBALL, [{"id": "fig_1", "graphics": ["Figures/missing"]}])

    assert assets == {}


def test_an_extension_already_written_out_still_resolves():
    assets = extract_assets(TARBALL, [{"id": "fig_1",
                                       "graphics": ["Figures/ModalNet-21.png"]}])

    assert assets == {"Figures/ModalNet-21.png": PNG}


def test_the_pack_records_the_asset_each_figure_resolved_to():
    """Without the resolved name the dashboard has to re-guess the extension."""
    pack = _pack_from_tarball(TARBALL, source="arXiv:1706.03762")

    assert pack["figures"][0]["assets"] == ["Figures/ModalNet-21.png"]


def test_a_figure_whose_image_is_absent_reports_no_assets():
    tarball = _tarball({"main.tex": PAPER})

    pack = _pack_from_tarball(tarball, source="x")

    assert pack["figures"][0]["assets"] == []
    assert pack["figures"][0]["caption"] == "The Transformer - model architecture."


def test_build_pack_never_returns_bytes_in_the_pack(tmp_path):
    """pack.json is a JSON document. Image bytes inside it make the whole pack
    unserialisable, which would have failed at the very end of a long run."""
    import json

    from paper_skill.paper2pack import build_pack

    class _Resp:
        content = TARBALL
        def raise_for_status(self): pass

    pack = build_pack("arXiv:1706.03762", get=lambda *a, **k: _Resp(),
                      assets_dir=tmp_path)

    json.dumps(pack)                       # must not raise
    assert "assets" not in pack


def test_the_images_are_written_where_they_were_asked_for(tmp_path):
    from paper_skill.paper2pack import build_pack

    class _Resp:
        content = TARBALL
        def raise_for_status(self): pass

    pack = build_pack("arXiv:1706.03762", get=lambda *a, **k: _Resp(),
                      assets_dir=tmp_path)

    written = tmp_path / "Figures" / "ModalNet-21.png"
    assert written.read_bytes() == PNG
    assert pack["figures"][0]["assets"] == ["Figures/ModalNet-21.png"]


def test_without_an_assets_dir_nothing_is_written_but_names_survive():
    """P1 can be run just to inspect a pack; that must not litter the cwd."""
    from paper_skill.paper2pack import build_pack

    class _Resp:
        content = TARBALL
        def raise_for_status(self): pass

    pack = build_pack("arXiv:1706.03762", get=lambda *a, **k: _Resp())

    assert pack["figures"][0]["assets"] == ["Figures/ModalNet-21.png"]
    assert "assets" not in pack


import pytest

fitz = pytest.importorskip("fitz")


def _one_page_pdf() -> bytes:
    doc = fitz.open()
    doc.new_page(width=120, height=60).insert_text((10, 30), "residual block")
    return doc.tobytes()


def test_a_pdf_figure_is_rasterised_so_a_browser_can_show_it():
    """LaTeX figures are very often PDF -- all 7 of ResNet's and all 13 of
    DDIM's are -- and no browser renders a PDF in an <img>. PyMuPDF is already
    a dependency for the PDF rung, and block.pdf came out smaller as a PNG
    (399.7 KB -> 11.9 KB)."""
    figures = [{"id": "fig_1", "graphics": ["eps/block"]}]

    assets = extract_assets(_tarball({"eps/block.pdf": _one_page_pdf()}), figures)

    assert list(assets) == ["eps/block.png"]
    assert assets["eps/block.png"].startswith(b"\x89PNG")
    assert figures[0]["assets"] == ["eps/block.png"]


def test_a_png_is_left_exactly_as_it_was():
    """Only what a browser cannot show gets converted."""
    figures = [{"id": "fig_1", "graphics": ["Figures/ModalNet-21"]}]

    assets = extract_assets(TARBALL, figures)

    assert assets["Figures/ModalNet-21.png"] == PNG


def test_an_unreadable_pdf_is_kept_rather_than_dropped():
    """A figure we cannot rasterise is still evidence the figure exists; the
    dashboard can skip it. Losing it silently is the worse failure."""
    figures = [{"id": "fig_1", "graphics": ["eps/broken"]}]

    assets = extract_assets(_tarball({"eps/broken.pdf": b"not a pdf at all"}), figures)

    assert figures[0]["assets"] == ["eps/broken.pdf"]
    assert assets["eps/broken.pdf"] == b"not a pdf at all"


def test_a_dot_slash_prefix_still_finds_the_file():
    """AIAYN writes \includegraphics{./vis/anaphora_resolution_new.pdf} while
    the tarball member is vis/anaphora_resolution_new.pdf. Normalising only the
    member name left the paper's attention visualisations -- its most
    pedagogically valuable figures -- resolving to nothing."""
    figures = [{"id": "fig_1", "graphics": ["./vis/anaphora_resolution_new.pdf"]}]

    assets = extract_assets(
        _tarball({"vis/anaphora_resolution_new.pdf": _one_page_pdf()}), figures)

    assert figures[0]["assets"] == ["vis/anaphora_resolution_new.png"]
    assert assets["vis/anaphora_resolution_new.png"].startswith(b"\x89PNG")


def test_a_member_stored_with_a_dot_slash_is_also_found():
    """Tarballs write member names both ways; only one side was normalised."""
    figures = [{"id": "fig_1", "graphics": ["Figures/ModalNet-21"]}]

    assets = extract_assets(_tarball({"./Figures/ModalNet-21.png": PNG}), figures)

    assert assets == {"Figures/ModalNet-21.png": PNG}
