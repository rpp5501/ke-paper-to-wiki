"""Tables from the non-LaTeX readers.

ar5iv gives real markup -- <tr> and <td> -- so its rows are recoverable exactly.
The PDF reader deliberately does not try: PyMuPDF's table finder, run against a
real 19-page paper, reported ordinary sentences as a table and collapsed the
genuine results grid's columns into single cells. A number sitting against the
wrong condition is a fabricated result, and the evidence rules forbid it.
"""
import pytest

selectolax = pytest.importorskip("selectolax")

from paper_skill.paper2pack import _pack_from_ar5iv  # noqa: E402

# ar5iv wraps a tabular in a figure and keeps the caption in a figcaption.
AR5IV = b"""
<html><head><title>A Paper</title></head><body>
<h2>Experiments</h2>
<figure class="ltx_table">
<figcaption>Table 1: BLEU on newstest2014.</figcaption>
<table class="ltx_tabular">
<tr><th>Model</th><th>EN-DE</th><th>EN-FR</th></tr>
<tr><td>ByteNet</td><td>23.75</td><td></td></tr>
<tr><td>Transformer (big)</td><td>28.4</td><td>41.8</td></tr>
</table>
</figure>
</body></html>
"""


def _tables():
    return _pack_from_ar5iv(AR5IV, "arXiv:test")["tables"]


def test_ar5iv_rows_are_recovered_exactly():
    table = _tables()[0]

    assert table["rows"][0] == ["Model", "EN-DE", "EN-FR"]
    assert table["rows"][-1] == ["Transformer (big)", "28.4", "41.8"]


def test_ar5iv_caption_comes_from_the_enclosing_figure():
    assert _tables()[0]["caption"] == "Table 1: BLEU on newstest2014."


def test_ar5iv_table_is_attributed_to_its_section():
    assert _tables()[0]["section"] == "sec_1"


def test_ar5iv_reports_exact_table_fidelity():
    pack = _pack_from_ar5iv(AR5IV, "arXiv:test")

    assert pack["extraction"]["table_fidelity"] == "exact"


def test_a_layout_table_with_no_cells_is_not_emitted():
    """ar5iv uses tables for layout too; an empty one is not evidence."""
    html = b"<html><body><h2>S</h2><table><tr></tr></table></body></html>"

    assert _pack_from_ar5iv(html, "x")["tables"] == []


def test_pdf_path_declares_that_it_did_not_try():
    """The absence of tables in a PDF pack is a limitation of the reader, not
    a fact about the paper, and downstream has to be able to tell."""
    fitz = pytest.importorskip("fitz")  # noqa: F841
    from pathlib import Path

    from paper_skill.paper2pack import _pack_from_pdf

    pdf = Path(__file__).resolve().parents[2] / "2504.04033v1.pdf"
    if not pdf.exists():
        pytest.skip("sample PDF not present")

    pack = _pack_from_pdf(str(pdf), "arXiv:2504.04033")

    assert pack["tables"] == []
    assert pack["extraction"]["table_fidelity"] == "none"


# --- .bib fallback -----------------------------------------------------------

def test_a_tarball_with_only_a_bib_still_yields_references():
    r"""arXiv:2607.05316 ships bibliography.bib and submission.tex with
    \bibliography{...} and no .bbl, because arXiv runs BibTeX itself at build
    time. The reader looked only for a .bbl or an inline thebibliography and
    produced zero references for a paper with 32 of them and 23 \cite calls.
    """
    import io
    import tarfile

    from paper_skill.paper2pack import _pack_from_tarball

    tex = (r"\documentclass{article}\begin{document}\section{S}"
           r"Prose citing \citep{arditi2024refusal}."
           r"\bibliography{bibliography}\end{document}")
    bib = ("@inproceedings{arditi2024refusal,\n"
           "title={Refusal in Language Models Is Mediated by a Single Direction},\n"
           "author={Andy Arditi and Neel Nanda},\nyear={2024}\n}\n")

    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as tf:
        for name, body in (("submission.tex", tex), ("bibliography.bib", bib)):
            data = body.encode("utf-8")
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))

    pack = _pack_from_tarball(buf.getvalue(), source="t")

    assert [r["key"] for r in pack["references"]] == ["arditi2024refusal"]
    assert "Refusal in Language Models" in pack["references"][0]["text"]


def test_a_bbl_still_wins_over_a_bib_when_both_are_present():
    """The .bbl is what the paper actually rendered -- it carries the numbering
    and any hand edits. The .bib is the fallback, not the preference."""
    import io
    import tarfile

    from paper_skill.paper2pack import _pack_from_tarball

    tex = r"\documentclass{article}\begin{document}\section{S}x\end{document}"
    bbl = (r"\begin{thebibliography}{1}" "\n"
           r"\bibitem[A(2024)]{from_bbl} The rendered one." "\n"
           r"\end{thebibliography}" "\n")
    bib = "@misc{from_bib, title={The fallback one}, year={2024}}\n"

    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as tf:
        for name, body in (("main.tex", tex), ("main.bbl", bbl),
                           ("refs.bib", bib)):
            data = body.encode("utf-8")
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))

    pack = _pack_from_tarball(buf.getvalue(), source="t")

    assert [r["key"] for r in pack["references"]] == ["from_bbl"]
