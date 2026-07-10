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


BBL_TRUNCATED = r"""
\begin{thebibliography}{10}
\bibitem{bahdanau2014} Dzmitry Bahdanau, et al. Neural machine translation.
arXiv:1409.0473, 2014.
\bibitem{he2016} Kaiming He, et al. Deep residual learning. CVPR 2016.
"""


def test_last_item_kept_without_end_terminator():
    refs = parse_bbl(BBL_TRUNCATED)
    assert len(refs) == 2
    assert refs[-1]["key"] == "he2016"
    assert "residual" in refs[-1]["text"]
    assert "CVPR 2016." in refs[-1]["text"]
