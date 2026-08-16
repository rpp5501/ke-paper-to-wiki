"""Structured .bbl parse (§15 token hygiene: never haul raw citation text)."""
import re

_ARXIV = re.compile(r"arXiv[:\s]*(\d{4}\.\d{4,5})", re.I)

# BibTeX puts the id in its own field rather than in prose, so the _ARXIV
# pattern above never sees it.
_EPRINT = re.compile(r"\beprint\s*=\s*[{\"]\s*(\d{4}\.\d{4,5})", re.I)
# @string and @comment declare macros, not works cited.
_NOT_A_WORK = {"string", "comment", "preamble"}
# The fields worth carrying into the pack: what a reader needs to recognise the
# work. Everything else (publisher, pages, doi internals) is token cost.
_BIB_FIELDS = ("title", "author", "booktitle", "journal", "year")


def _bib_field(body: str, name: str) -> str:
    """One brace- or quote-delimited BibTeX field value, braces stripped."""
    m = re.search(rf"\b{name}\s*=\s*", body, re.I)
    if not m:
        return ""
    rest = body[m.end():].lstrip()
    if not rest[:1] in "{\"":
        return " ".join(rest.split(",", 1)[0].split())
    close, depth, out = ("}" if rest[0] == "{" else "\""), 0, []
    for ch in rest:
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                break
        elif ch == "\"" and close == "\"" and out:
            break
        out.append(ch)
    return " ".join("".join(out).lstrip("{\"").replace("{", "").replace("}", "").split())


def parse_bib(bib_text: str) -> list[dict]:
    r"""References straight from a .bib, for papers that ship no .bbl.

    arXiv:2607.05316 ships bibliography.bib plus a \bibliography{...} call and
    lets arXiv run BibTeX at build time, so there is no .bbl in the source at
    all. The tarball reader looked only for a .bbl or an inline
    thebibliography and returned zero references for a paper with 32 of them.
    """
    refs = []
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,\s}]+)\s*,", bib_text or ""):
        kind, key = m.group(1).lower(), m.group(2)
        if kind in _NOT_A_WORK:
            continue
        nxt = bib_text.find("@", m.end())
        body = bib_text[m.end():nxt if nxt != -1 else len(bib_text)]
        parts = [v for v in (_bib_field(body, f) for f in _BIB_FIELDS) if v]
        text = ". ".join(parts)
        eprint = _EPRINT.search(body) or _ARXIV.search(body)
        refs.append({"key": key, "text": text,
                     "arxiv_id": eprint.group(1) if eprint else None})
    return refs


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
