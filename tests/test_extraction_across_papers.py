"""Extraction defects that only a paper outside the four on disk would reveal.

Every one of these produced a pack that looked healthy -- status ok, path
latex, equation_fidelity exact -- while missing most or all of the paper. They
were found by running P1 over eight arXiv papers with no LLM in the loop, and
each is pinned here with the smallest input that reproduces it.
"""
import io
import tarfile

from paper_skill.latex_pack import latex_to_pack
from paper_skill.paper2pack import _pack_from_tarball
from paper_skill.references import parse_bbl

# Both conference style files really do contain the string, in the usage
# comment at the top: "\documentclass{article}" and similar.
CVPR_STY = r"""
%% cvpr.sty -- for use with \documentclass[10pt,twocolumn]{article}
\typeout{CVPR style}
\section{ThisIsNotThePaper}
"""

PAPER_TEX = r"""
\documentclass{article}
\usepackage{cvpr}
\title{Deep Residual Learning for Image Recognition}
\begin{document}
\section{Introduction}
Deeper networks are harder to train.
\begin{equation}\mathcal{F}(x) + x\end{equation}
\end{document}
"""


def _tarball(members: dict) -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as tf:
        for name, text in members.items():
            data = text.encode("utf-8")
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))
    return buf.getvalue()


def test_style_file_is_not_mistaken_for_the_paper():
    """cvpr.sty sorted ahead of the paper and won on "contains \\documentclass",
    so ResNet packed as 2 sections and 0 equations -- stamped exact."""
    pack = _pack_from_tarball(
        _tarball({"cvpr.sty": CVPR_STY, "residual_arxiv.tex": PAPER_TEX}),
        source="arXiv:1512.03385")

    assert pack["meta"]["title"] == "Deep Residual Learning for Image Recognition"
    assert [s["title"] for s in pack["sections"]] == ["Introduction"]
    assert len(pack["equations"]) == 1


def test_a_submission_with_only_a_style_file_still_returns_something():
    """The .tex preference must not turn a degenerate tarball into a crash --
    _require_content is the stage that decides an empty pack is a failure."""
    pack = _pack_from_tarball(_tarball({"cvpr.sty": CVPR_STY}), source="x")

    assert "sections" in pack


def test_natbib_bibitem_with_an_optional_label_is_parsed():
    """natbib writes \\bibitem[Song et al.(2020)]{song2020}. Requiring the brace
    to follow immediately silently yielded zero references on six of the eight
    papers sampled -- every ICLR and ICML one."""
    bbl = (r"\begin{thebibliography}{10}"
           "\n"
           r"\bibitem[Song et~al.(2020)Song, Meng, and Ermon]{song2020denoising}"
           "\nJiaming Song, Chenlin Meng, and Stefano Ermon.\n"
           r"\newblock Denoising diffusion implicit models, arXiv:2010.02502."
           "\n"
           r"\bibitem[He et~al.(2016)]{he2016deep}"
           "\nKaiming He et~al. Deep residual learning.\n"
           r"\end{thebibliography}")

    refs = parse_bbl(bbl)

    assert [r["key"] for r in refs] == ["song2020denoising", "he2016deep"]
    assert refs[0]["arxiv_id"] == "2010.02502"
    assert "Denoising diffusion" in refs[0]["text"]


def test_plain_bibitem_still_parses():
    """The optional group is optional -- the old form must keep working."""
    refs = parse_bbl(r"\bibitem{vaswani2017} Ashish Vaswani et al. arXiv:1706.03762.")

    assert refs[0]["key"] == "vaswani2017"
    assert refs[0]["arxiv_id"] == "1706.03762"


def test_icml_title_macro_is_read():
    """ICML papers never call \\title; the style file defines \\icmltitle, and
    pylatexenc has no spec for it, so the walker reports no argument at all."""
    pack = latex_to_pack(
        r"\documentclass{article}"
        "\n"
        r"\icmltitle{Sequence Transduction with Recurrent Neural Networks}"
        "\n"
        r"\begin{document}\section{Intro}Text.\end{document}")

    assert pack["meta"]["title"] == ("Sequence Transduction with "
                                     "Recurrent Neural Networks")


def test_a_title_that_is_itself_a_macro_stays_empty():
    """\\icmltitle{\\titl} cannot be expanded without running TeX. Empty is
    honest; the literal string "\\titl" would be a fabricated title."""
    pack = latex_to_pack(r"\documentclass{article}\icmltitle{\titl}"
                         r"\begin{document}\section{S}T.\end{document}")

    assert pack["meta"]["title"] == ""


def test_plain_title_still_wins():
    pack = latex_to_pack(r"\documentclass{article}\title{Attention Is All You Need}"
                         r"\begin{document}\section{S}T.\end{document}")

    assert pack["meta"]["title"] == "Attention Is All You Need"
