"""Results tables survive extraction.

Every pack in artifacts/ carried figures=0 and no tables key at all, so an
empirical paper's evidence never reached the page writer. The table environment
was walked like any other, which poured its cells into the surrounding prose as
one run-on line: the numbers arrived, unusable.
"""
from paper_skill.latex_pack import latex_to_pack
from paper_skill.p4_context import assemble_context

TEX = r"""
\section{Experiments}
We evaluate on two datasets.
\begin{table}[t]
\caption{BLEU on newstest2014.}
\begin{tabular}{lcc}
\toprule
Model & EN-DE & EN-FR \\
\midrule
ByteNet & 23.75 & \\
\textbf{Transformer (big)} & \textbf{28.4} & \textbf{41.8} \\
\bottomrule
\end{tabular}
\end{table}
The big model wins on both pairs.
"""

# The shapes an actual results table is written in: booktabs rules, table*,
# column rules, multicolumn spans, math cells carrying a spread, and escapes.
MESSY = r"""
\section{Results}
\begin{table*}[htbp]
\caption{Attack accuracy (\%) on \textit{Census}, mean $\pm$ s.d.}
\begin{tabular}{l|cc|c}
\toprule
\multicolumn{2}{c}{Setting} & \multicolumn{2}{c}{Accuracy} \\
\cmidrule(lr){1-2}
Method & $k$ & Overall & High-risk \\
\midrule
Baseline & 5 & $62.1 \pm 0.4$ & 48.0 \\
Ours & 5 & $\mathbf{91.4} \pm 0.2$ & \textbf{88.7} \\
R\&D note & 10 & 70.5 & 66.1 \\
\bottomrule
\end{tabular}
\end{table*}
"""


def _pack():
    return latex_to_pack(TEX, resolve_input=lambda n: "")


def test_table_rows_and_caption_are_captured():
    table = _pack()["tables"][0]

    assert table["id"] == "tab_1"
    assert table["section"] == "sec_1"
    assert table["caption"] == "BLEU on newstest2014."
    assert ["Model", "EN-DE", "EN-FR"] == table["rows"][0]
    assert ["Transformer (big)", "28.4", "41.8"] == table["rows"][-1]


def test_rule_macros_do_not_become_rows():
    rows = _pack()["tables"][0]["rows"]

    assert len(rows) == 3
    assert all(any(cell for cell in row) for row in rows)


def test_cells_no_longer_smear_into_the_section_prose():
    """The regression this fixes: 28.4 used to land in the paragraph text."""
    text = _pack()["sections"][0]["text"]

    assert "We evaluate on two datasets." in text
    assert "The big model wins" in text
    assert "28.4" not in text
    assert "toprule" not in text


def test_a_table_without_a_tabular_still_reports_its_caption():
    tex = (r"\section{Results}"
           r"\begin{table}\caption{Accuracy, plotted.}"
           r"\includegraphics{plot.png}\end{table}")

    table = latex_to_pack(tex, resolve_input=lambda n: "")["tables"][0]

    assert table["caption"] == "Accuracy, plotted."
    assert table["rows"] == []


def test_tables_reach_the_writers_local_context():
    """Extraction alone changes nothing if the numbers stop at the pack."""
    pack = _pack()
    graph = {"nodes": [{"id": "experiments", "label": "Experiments",
                        "source_ref": "sec_1"}], "edges": []}

    context = assemble_context(pack, graph, "experiments", None)

    assert "BLEU on newstest2014." in context["local_slice"]
    assert "28.4" in context["local_slice"]
    assert "41.8" in context["local_slice"]


def test_a_caption_only_table_is_not_offered_as_evidence():
    """No rows means no numbers; do not hand the writer an empty table to
    reproduce, or it will describe one it cannot see."""
    tex = (r"\section{Results}\begin{table}\caption{Plotted.}"
           r"\includegraphics{p.png}\end{table}")
    pack = latex_to_pack(tex, resolve_input=lambda n: "")
    graph = {"nodes": [{"id": "r", "label": "R", "source_ref": "sec_1"}], "edges": []}

    assert "Plotted." not in assemble_context(pack, graph, "r", None)["local_slice"]


def test_real_world_table_markup_survives():
    table = latex_to_pack(MESSY, resolve_input=lambda n: "")["tables"][0]

    assert table["caption"] == r"Attack accuracy (%) on Census, mean $\pm$ s.d."
    # \cmidrule's span argument used to arrive glued to the next header cell
    assert table["rows"][1][0] == "Method"
    # an escaped ampersand is a character, not a column separator
    assert table["rows"][-1][0] == "R&D note"
    # bold wrappers come off; the math carrying the spread stays
    assert table["rows"][3] == ["Ours", "5", r"$91.4 \pm 0.2$", "88.7"]


def test_math_in_cells_is_not_flattened_away():
    table = latex_to_pack(MESSY, resolve_input=lambda n: "")["tables"][0]

    assert any(r"\pm" in cell for row in table["rows"] for cell in row)
