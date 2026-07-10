from paper_skill.references import parse_bbl

BBL = r"""
\begin{thebibliography}{10}
\bibitem{bahdanau2014} Dzmitry Bahdanau, et al. Neural machine translation.
arXiv:1409.0473, 2014.
\bibitem{he2016} Kaiming He, et al. Deep residual learning. CVPR 2016.
\end{thebibliography}
"""


def test_two_items_with_keys_and_arxiv_id():
    refs = parse_bbl(BBL)
    assert len(refs) == 2
    assert refs[0]["key"] == "bahdanau2014"
    assert refs[0]["arxiv_id"] == "1409.0473"
    assert refs[1]["arxiv_id"] is None
    assert "residual" in refs[1]["text"]
