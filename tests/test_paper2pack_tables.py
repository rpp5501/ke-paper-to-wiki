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
