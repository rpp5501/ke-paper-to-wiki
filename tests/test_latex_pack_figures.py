"""The paper's own figures are the best visual explanation it has, and until
now latex_to_pack returned a hardcoded empty list for every paper. AIAYN ships
6 figure environments and 12 images inside its e-print tarball; the dashboard
had none of them, and a hand-drawn mermaid substitute stood in for Figure 1.
"""
from paper_skill.latex_pack import latex_to_pack

ARCH = r"""\documentclass{article}\begin{document}
\section{Model Architecture}
Most competitive models have an encoder-decoder structure.
\begin{figure}
\centering
\includegraphics[scale=0.6]{Figures/ModalNet-21}
\caption{The Transformer - model architecture.}
\label{fig:model-arch}
\end{figure}
\end{document}"""


def test_a_figure_is_extracted_with_its_caption_and_graphic():
    figures = latex_to_pack(ARCH)["figures"]

    assert len(figures) == 1
    assert figures[0]["id"] == "fig_1"
    assert figures[0]["caption"] == "The Transformer - model architecture."
    assert figures[0]["graphics"] == ["Figures/ModalNet-21"]
    assert figures[0]["section"] == "sec_1"


def test_the_figure_body_does_not_smear_into_the_section_prose():
    """The same defect tables had: walking the environment dumped its innards
    into the surrounding text, so the prose carried filenames and scale
    factors."""
    text = latex_to_pack(ARCH)["sections"][0]["text"]

    assert "encoder-decoder structure" in text
    assert "ModalNet" not in text
    assert "includegraphics" not in text


STARRED = r"""\documentclass{article}\begin{document}
\section{Attention}
\begin{figure*}
\includegraphics[width=0.4\textwidth]{Figures/ModalNet-19}
\includegraphics[width=0.4\textwidth]{Figures/ModalNet-20}
\caption{Scaled Dot-Product Attention and Multi-Head Attention.}
\end{figure*}
\end{document}"""


def test_a_two_column_figure_with_several_graphics_keeps_all_of_them():
    """figure* is how a wide figure spans both columns, and side-by-side
    subfigures are one environment with several includegraphics."""
    figures = latex_to_pack(STARRED)["figures"]

    assert len(figures) == 1
    assert figures[0]["graphics"] == ["Figures/ModalNet-19", "Figures/ModalNet-20"]
    assert "Multi-Head Attention" in figures[0]["caption"]


def test_a_figure_with_no_graphic_is_still_reported():
    """A TikZ figure draws itself and includes no file. The caption alone tells
    the writer the figure exists, which is what tables already do."""
    tikz = (r"\documentclass{article}\begin{document}\section{S}"
            r"\begin{figure}\begin{tikzpicture}\draw (0,0) -- (1,1);"
            r"\end{tikzpicture}\caption{A causal DAG.}\end{figure}\end{document}")

    figures = latex_to_pack(tikz)["figures"]

    assert len(figures) == 1
    assert figures[0]["caption"] == "A causal DAG."
    assert figures[0]["graphics"] == []


def test_a_paper_with_no_figures_reports_none():
    plain = r"\documentclass{article}\begin{document}\section{S}Text.\end{document}"

    assert latex_to_pack(plain)["figures"] == []


def test_captionof_does_not_yield_the_word_figure():
    """The caption package's \captionof{figure}{Real caption} starts with the
    same eight characters as \caption, so a prefix search took its FIRST group
    -- DDIM shipped a figure whose caption was the literal string "figure"."""
    tex = (r"\documentclass{article}\begin{document}\section{S}"
           r"\begin{figure}\includegraphics{figures/acc.pdf}"
           r"\captionof{figure}{Accuracy against the number of steps.}"
           r"\end{figure}\end{document}")

    figures = latex_to_pack(tex)["figures"]

    assert figures[0]["caption"] == "Accuracy against the number of steps."


def test_a_short_caption_for_the_list_of_figures_is_not_the_caption():
    """\caption[short]{the real one} puts the short form in the LoF."""
    tex = (r"\documentclass{article}\begin{document}\section{S}"
           r"\begin{figure}\includegraphics{a.png}"
           r"\caption[Transformer]{The Transformer - model architecture.}"
           r"\end{figure}\end{document}")

    assert latex_to_pack(tex)["figures"][0]["caption"] == (
        "The Transformer - model architecture.")
