"""Structured .bbl parse (§15 token hygiene: never haul raw citation text)."""
import re

_ARXIV = re.compile(r"arXiv[:\s]*(\d{4}\.\d{4,5})", re.I)


def parse_bbl(bbl_text: str) -> list[dict]:
    refs = []
    # natbib writes \bibitem[Song et al.(2020)]{song2020}. Requiring the brace
    # to follow \bibitem immediately meant every natbib .bbl parsed to zero
    # references while the file itself was found and looked fine -- six of
    # eight sampled arXiv papers, including every ICLR and ICML one.
    for m in re.finditer(r"\\bibitem\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}"
                         r"(.*?)(?=\\bibitem\b|\\end\{thebibliography\}|\Z)",
                         bbl_text, re.S):
        text = " ".join(m.group(2).split())
        ax = _ARXIV.search(text)
        refs.append({"key": m.group(1), "text": text,
                     "arxiv_id": ax.group(1) if ax else None})
    return refs
