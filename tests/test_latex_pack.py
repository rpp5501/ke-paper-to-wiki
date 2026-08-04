from paper_skill.latex_pack import latex_to_pack

TEX = r"""
\section{Model Architecture}
Intro text here.
\subsection{Attention}
An attention function.
\begin{equation}
\mathrm{Attention}(Q,K,V)=\mathrm{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V
\end{equation}
\input{extra}
"""


def test_sections_form_numbered_tree():
    pack = latex_to_pack(TEX, resolve_input=lambda n: r"\section{Extra}Tail.")
    ids = [s["id"] for s in pack["sections"]]
    assert ids == ["sec_1", "sec_1_1", "sec_2"]
    assert pack["sections"][1]["title"] == "Attention"
    assert pack["sections"][1]["level"] == 2


def test_equation_latex_is_verbatim_and_anchored():
    pack = latex_to_pack(TEX, resolve_input=lambda n: "")
    eq = pack["equations"][0]
    assert eq["id"] == "eq_1"
    assert r"\sqrt{d_k}" in eq["latex"]
    assert eq["section"] == "sec_1_1"


def test_extraction_block_says_exact():
    pack = latex_to_pack(TEX, resolve_input=lambda n: "")
    assert pack["extraction"] == {"path": "latex", "equation_fidelity": "exact"}


# The title is not cosmetic: it is interpolated into CONCEPT_PROMPT as
# "Paper: {title}", so a blank one silently degrades every rung-1 extraction.
TITLED = r"""
\title{Structural Intervention Distance for Evaluating Causal Graphs}
\author{Someone}
\begin{document}
\maketitle
\section{Introduction}
Body.
\end{document}
"""


def test_title_is_parsed_from_the_tex():
    assert latex_to_pack(TITLED)["meta"]["title"] == (
        "Structural Intervention Distance for Evaluating Causal Graphs")


def test_explicit_title_wins_over_the_tex():
    """A caller that already knows the title (e.g. the PDF-sibling upgrade
    path) must not have it overwritten by the source."""
    pack = latex_to_pack(TITLED, title="Known From OpenAlex")
    assert pack["meta"]["title"] == "Known From OpenAlex"


def test_title_survives_line_breaks_and_nested_macros():
    tex = r"\title{SID for Evaluating\\ \emph{Causal} Graphs}" + "\n" + TEX
    assert latex_to_pack(tex, resolve_input=lambda n: "")["meta"]["title"] == (
        "SID for Evaluating Causal Graphs")


def test_missing_title_stays_empty_rather_than_guessing():
    assert latex_to_pack(TEX, resolve_input=lambda n: "")["meta"]["title"] == ""
