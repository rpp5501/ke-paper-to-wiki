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


# --- raw BibTeX --------------------------------------------------------------
# arXiv:2607.05316 ships bibliography.bib and submission.tex with
# \bibliography{...}, and no .bbl -- arXiv runs BibTeX itself at build time.
# _pack_from_tarball looked only for a .bbl or an inline thebibliography, found
# neither, and returned zero references for a paper with 32 of them and 23
# \cite calls. Any paper shipping raw BibTeX loses its whole bibliography.

BIB = r"""
@inproceedings{
arditi2024refusal,
title={Refusal in Language Models Is Mediated by a Single Direction},
author={Andy Arditi and Oscar Balcells Obeso and Neel Nanda},
booktitle={The Thirty-eighth Annual Conference on Neural Information Processing Systems},
year={2024},
url={https://openreview.net/forum?id=pH3XAQME6c}
}

@misc{burns2023ccs,
      title={Discovering Latent Knowledge in Language Models Without Supervision},
      author={Collin Burns and Haotian Ye},
      year={2023},
      eprint={2212.03827},
      archivePrefix={arXiv}
}

% a stray comment, and a string macro that is not a reference
@string{neurips = "NeurIPS"}
"""


def test_bib_entries_are_parsed_when_there_is_no_bbl():
    from paper_skill.references import parse_bib

    refs = parse_bib(BIB)

    assert [r["key"] for r in refs] == ["arditi2024refusal", "burns2023ccs"]


def test_a_bib_reference_carries_its_title_and_authors():
    """The text field is what reaches the writer; a key alone is useless."""
    from paper_skill.references import parse_bib

    first = parse_bib(BIB)[0]

    assert "Refusal in Language Models" in first["text"]
    assert "Arditi" in first["text"] or "Andy Arditi" in first["text"]


def test_an_eprint_field_yields_the_arxiv_id():
    """BibTeX records the id in `eprint=`, not as "arXiv:NNNN.NNNNN" prose, so
    the .bbl regex alone would miss every one of them."""
    from paper_skill.references import parse_bib

    burns = next(r for r in parse_bib(BIB) if r["key"] == "burns2023ccs")

    assert burns["arxiv_id"] == "2212.03827"


def test_string_macros_and_comments_are_not_references():
    from paper_skill.references import parse_bib

    assert all(r["key"] != "neurips" for r in parse_bib(BIB))


def test_an_empty_or_garbage_bib_yields_nothing_rather_than_raising():
    from paper_skill.references import parse_bib

    assert parse_bib("") == []
    assert parse_bib("not bibtex at all {{{") == []
