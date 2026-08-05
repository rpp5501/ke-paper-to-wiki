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


# --- Renderable math -------------------------------------------------------
#
# The pack's LaTeX is copied VERBATIM into pages and handed straight to KaTeX.
# Measured on arXiv:1306.1043, 8 of 11 equations threw and the reader was shown
# raw LaTeX instead of maths. Two causes, both general to LaTeX rather than to
# that paper: \label is cross-reference bookkeeping KaTeX has no command for,
# and an align/eqnarray BODY keeps the & and \ that only mean something inside
# the wrapper this extractor drops. A third, blank lines, is our own artefact:
# _strip_comments deletes % lines and leaves the holes behind, and a blank line
# is invalid inside LaTeX math anyway -- it also ends the markdown paragraph,
# tearing the $$ block in half.

from paper_skill.latex_pack import normalize_math


def _wrapped(latex):
    return latex.startswith(r"\begin{aligned}") and latex.endswith(r"\end{aligned}")


def test_label_is_stripped():
    assert normalize_math(r"\label{eq:foo}x = 1") == "x = 1"


def test_nonumber_and_notag_are_stripped():
    assert normalize_math(r"x = 1 \nonumber") == "x = 1"
    assert normalize_math(r"x = 1 \notag") == "x = 1"


def test_align_body_is_wrapped_so_its_ampersands_have_a_home():
    out = normalize_math(r"a &= b \\ c &= d")
    assert _wrapped(out)
    assert "a &= b" in out


def test_row_breaks_alone_are_enough_to_need_alignment():
    r"""A gather/multline body has \\ but no & and is equally unrenderable bare."""
    assert _wrapped(normalize_math(r"a = b \\ c = d"))


def test_an_environment_that_already_owns_its_ampersands_is_left_alone():
    """array/aligned/cases bodies are already valid; wrapping would nest badly."""
    out = normalize_math(r"\begin{array}{rcl} a &=& b \\ c &=& d \end{array}")
    assert not _wrapped(out)


def test_an_ampersand_outside_a_nested_environment_still_needs_wrapping():
    """The failing shape a containment check misses: the body HAS an
    environment, but the alignment marker sits after it, at top level."""
    assert _wrapped(normalize_math(
        r"\left\{ \begin{array}{c} p \\ q \end{array} \right\} &= r"))


def test_an_escaped_ampersand_is_not_an_alignment_marker():
    assert not _wrapped(normalize_math(r"\text{Smith \& Jones} = 1"))


def test_a_row_break_inside_an_environment_does_not_trigger_wrapping():
    assert not _wrapped(normalize_math(
        r"\begin{cases} a \\ b \end{cases}"))


def test_blank_lines_are_collapsed():
    """Left by _strip_comments; invalid in LaTeX math and fatal to the $$ block."""
    assert "\n\n" not in normalize_math("a = b \\\\\n\n\n\nc = d")


def test_normalizing_twice_changes_nothing():
    once = normalize_math(r"\label{e}a &= b \\ c &= d")
    assert normalize_math(once) == once


# Bookkeeping hides one level up too. arXiv:1312.6114 (VAE) defines
#   \newcommand{\eqnr}{\addtocounter{equation}{1}\tag{\theequation}}
# purely to number its equations. extract_macros exported it faithfully, KaTeX
# has no counters, and 22 of that paper's 30 equations died on it.
def test_a_numbering_only_macro_exports_empty():
    tex = "\n".join([
        r"\newcommand{\eqnr}{\addtocounter{equation}{1}\tag{\theequation}}",
        r"\section{S}", r"\begin{equation}", r"x = 1 \eqnr", r"\end{equation}"])
    assert latex_to_pack(tex)["macros"][r"\eqnr"] == ""


def test_a_macro_keeps_the_maths_around_its_bookkeeping():
    """Dropping the whole body would lose real notation."""
    tex = "\n".join([
        r"\newcommand{\myeq}[1]{\addtocounter{equation}{1}#1 = 0}",
        r"\section{S}", r"\begin{equation}", r"\myeq{y}", r"\end{equation}"])
    assert latex_to_pack(tex)["macros"][r"\myeq"] == "#1 = 0"


def test_an_ordinary_macro_is_untouched():
    tex = "\n".join([
        r"\newcommand{\R}{\mathbb{R}}",
        r"\section{S}", r"\begin{equation}", r"x \in \R", r"\end{equation}"])
    assert latex_to_pack(tex)["macros"][r"\R"] == r"\mathbb{R}"


def test_pack_equations_are_normalized_on_the_way_out():
    tex = "\n".join([r"\section{S}", r"\begin{align}",
                     r"\label{eq:x}a &= b \\ c &= d", r"\end{align}"])
    latex = latex_to_pack(tex)["equations"][0]["latex"]
    assert r"\label" not in latex
    assert _wrapped(latex)
