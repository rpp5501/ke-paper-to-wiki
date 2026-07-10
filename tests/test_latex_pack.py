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
