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


# Papers define their own notation in the preamble. latex_pack copies equations
# VERBATIM (equation_fidelity: "exact"), so dropping the macro table means the
# copied LaTeX references commands nothing downstream can resolve -- KaTeX
# throws and the reader sees a literal "\doo" instead of "do". All 11 equations
# of arXiv:1306.1043 were affected.
MACRO_TEX = r"""
\newcommand{\G}{\mathcal{G}}
\newcommand{\B}[1]{\mathbf{#1}}
\newcommand\lone{\ell_1}
\renewcommand{\vec}[1]{\mathbf{#1}}
\providecommand{\prob}{{\mathbb P}}
\DeclareMathOperator*{\SID}{SID}
\DeclareMathOperator{\doo}{do}
\section{Body}
Text.
"""


def test_macros_are_extracted_for_katex():
    macros = latex_to_pack(MACRO_TEX)["macros"]
    assert macros[r"\G"] == r"\mathcal{G}"
    assert macros[r"\lone"] == r"\ell_1"


def test_macro_arguments_are_preserved():
    """KaTeX uses the same #1 placeholder syntax, so the body passes through."""
    assert latex_to_pack(MACRO_TEX)["macros"][r"\B"] == r"\mathbf{#1}"


def test_renewcommand_and_providecommand_count_too():
    macros = latex_to_pack(MACRO_TEX)["macros"]
    assert macros[r"\vec"] == r"\mathbf{#1}"
    assert macros[r"\prob"] == r"{\mathbb P}"


def test_declaremathoperator_becomes_operatorname():
    macros = latex_to_pack(MACRO_TEX)["macros"]
    assert macros[r"\doo"] == r"\operatorname{do}"
    assert macros[r"\SID"] == r"\operatorname*{SID}"   # starred form takes limits


def test_nested_braces_in_a_body_are_read_whole():
    tex = r"\newcommand{\law}[1]{\mathcal{L}({#1})}" + "\n" + MACRO_TEX
    assert latex_to_pack(tex)["macros"][r"\law"] == r"\mathcal{L}({#1})"


def test_a_paper_with_no_macros_gets_an_empty_table():
    assert latex_to_pack(TEX, resolve_input=lambda n: "")["macros"] == {}


# KaTeX has no optional-argument macros at all: \newcommand{\q}[2][] throws
# outright. This paper's core notation is optional-arg -- \pa[\G]X reads
# "parents of X in graph G" -- over 51 call sites and 6 macros. Left alone,
# KaTeX takes "[" as the first argument and renders "pa][X".
OPT_TEX = "\n".join([
    r"\newcommand{\C}[1]{\mathcal{#1}}",
    r"\newcommand{\B}[1]{\mathbf{#1}}",
    r"\newcommand{\G}{\C{G}}",
    r"\newcommand{\pa}[2][]{{\B{pa}}^{#1}_{#2}}",
    r"\section{S}",
    r"\begin{equation}",
    r"p(\pa[]X) + q(\pa[\G]Y)",
    r"\end{equation}",
])


def test_optional_arg_call_sites_become_brace_calls():
    eq = latex_to_pack(OPT_TEX)["equations"][0]["latex"]
    assert r"\pa{}X" in eq
    assert r"\pa{\G}Y" in eq
    assert "[]" not in eq


def test_optional_arg_macro_is_still_exported_for_katex():
    assert latex_to_pack(OPT_TEX)["macros"][r"\pa"] == r"{\B{pa}}^{#1}_{#2}"


def test_brackets_after_an_ordinary_macro_are_left_alone():
    """Only macros DECLARED with an optional arg get rewritten — a bracket
    after any other macro is real content, e.g. an interval."""
    tex = OPT_TEX.replace(r"p(\pa[]X)", r"p(\G[0,1])")
    assert r"\G[0,1]" in latex_to_pack(tex)["equations"][0]["latex"]
