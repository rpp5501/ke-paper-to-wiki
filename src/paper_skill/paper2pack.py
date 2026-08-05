"""Fidelity-laddered router (§15). Rungs implemented: 1 latex, 2 ar5iv, 4 pdf."""
import argparse, io, json, os, re, sys, tarfile
from pathlib import Path
import requests
from .latex_pack import latex_to_pack, normalize_math
from .references import parse_bbl

UA = {"User-Agent": "paper-skill/0.1 (keyless research tool)"}
_ARXIV_ID = re.compile(r"^(arXiv:)?(\d{4}\.\d{4,5})(v\d+)?$")


def _no_apis() -> bool:
    return os.environ.get("RESEARCH_MCP_NO_APIS", "") == "1"


def detect(target: str) -> str:
    if _ARXIV_ID.match(target.strip()):
        return "arxiv"
    p = Path(target)
    if p.suffix == ".tex":
        return "tex"
    if p.suffix == ".pdf":
        return "pdf"
    return "unknown"


def _pack_from_tarball(blob: bytes, source: str) -> dict:
    tf = tarfile.open(fileobj=io.BytesIO(blob), mode="r:*")
    files = {m.name: tf.extractfile(m).read().decode("utf-8", "replace")
             for m in tf.getmembers() if m.isfile()}
    main = next((t for t in files.values() if "\\documentclass" in t),
                next(iter(files.values()), ""))
    def resolve(name):
        return files.get(name) or files.get(name + ".tex") or ""
    pack = latex_to_pack(main, resolve_input=resolve, source=source)
    bbl = next((t for n, t in files.items() if n.endswith(".bbl")), "")
    if not bbl:
        bbl = next((t for t in files.values() if r"\begin{thebibliography}" in t), "")
    if bbl:
        pack["references"] = parse_bbl(bbl)
    return pack


def _pack_from_ar5iv(html: bytes, source: str) -> dict:
    import datetime
    from selectolax.parser import HTMLParser
    doc = HTMLParser(html)
    sections, equations = [], []
    current_section = "sec_0"
    sec_n = eq_n = 0
    for node in doc.root.traverse():
        if node.tag in ("h2", "h3"):
            sec_n += 1
            current_section = f"sec_{sec_n}"
            sections.append({"id": current_section, "title": node.text(strip=True),
                             "level": 2 if node.tag == "h2" else 3, "text": ""})
        elif node.tag == "math" and node.attributes.get("alttext") is not None:
            eq_n += 1
            equations.append({"id": f"eq_{eq_n}",
                              "latex": normalize_math(node.attributes["alttext"]),
                              "section": current_section})
    return {"meta": {"source": source, "title": doc.css_first("title").text()
                     if doc.css_first("title") else "",
                     "generated": datetime.date.today().isoformat()},
            "extraction": {"path": "ar5iv", "equation_fidelity": "converted-mathml"},
            "sections": sections, "equations": equations,
            "references": [], "figures": []}


def _pack_from_pdf(path: str, source: str) -> dict:
    import datetime
    import fitz
    doc = fitz.open(path)
    pages = [page.get_text() or "" for page in doc]
    doc.close()
    body = "\n".join(pages)
    body = re.sub(r"-\n(?=[a-z])", "", body)             # de-hyphenate
    body = re.sub(r"^\s*\d+\s*$", "", body, flags=re.M)  # bare page numbers
    return {"meta": {"source": source, "title": Path(path).stem,
                     "generated": datetime.date.today().isoformat()},
            "extraction": {"path": "pdf", "equation_fidelity": "absent"},
            "sections": [{"id": "sec_1", "title": "full-text", "level": 1,
                          "text": " ".join(body.split())}],
            "equations": [], "references": [], "figures": []}


def _pdf_title(path: str) -> str:
    import fitz
    doc = fitz.open(path)
    title = (doc.metadata or {}).get("title") or ""
    title = title.strip()
    if title:
        doc.close()
        return title
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return Path(path).stem


class EmptyExtraction(ValueError):
    """A rung parsed cleanly and produced nothing."""


def _require_content(pack: dict) -> dict:
    """Refuse a pack with no sections and no equations.

    The ladder descends on exceptions only, so a rung that PARSED but yielded
    nothing used to be returned as a success. Both rungs did exactly that for
    arXiv:1412.6980 -- a wrapper .tex whose \\input targets are missing parses
    perfectly, and ar5iv serves an "Untitled Document" stub when its own
    conversion failed. Reported as path=latex either way, and P2 would then
    extract concepts from nothing: the TOC-shaped garbage the anti-TOC guard
    catches, arriving a stage earlier and cheaper.
    """
    if not pack.get("sections") and not pack.get("equations"):
        raise EmptyExtraction(pack.get("meta", {}).get("source", "pack"))
    return pack


def build_pack(target: str, get=requests.get, cache_dir=None) -> dict:
    kind = detect(target)
    if kind == "tex":
        return latex_to_pack(Path(target).read_text(encoding="utf-8"),
                             source=f"file:{target}")
    if kind == "pdf":
        if not _no_apis():
            from .upgrade import find_arxiv_sibling
            title = _pdf_title(target)
            ax = find_arxiv_sibling(title, get=get)
            if ax:
                return build_pack(ax, get=get, cache_dir=cache_dir)
        return _pack_from_pdf(target, source=f"file:{target}")
    if kind == "arxiv":
        if _no_apis():
            return {"status": "apis_disabled",
                    "hint": "arXiv download blocked by RESEARCH_MCP_NO_APIS — "
                            "pass a local .tex or .pdf instead"}
        arxiv_id = _ARXIV_ID.match(target.strip()).group(2)
        source = f"arXiv:{arxiv_id}"
        try:
            resp = get(f"https://arxiv.org/e-print/{arxiv_id}",
                       timeout=60, headers=UA)
            resp.raise_for_status()
            return _require_content(_pack_from_tarball(resp.content, source))
        except Exception:
            try:
                resp = get(f"https://ar5iv.labs.arxiv.org/html/{arxiv_id}",
                           timeout=60, headers=UA)
                resp.raise_for_status()
                return _require_content(_pack_from_ar5iv(resp.content, source))
            except EmptyExtraction:
                return {"status": "empty_extraction",
                        "hint": f"{source}: the e-print tarball and ar5iv both "
                                "parsed to nothing (ar5iv serves a stub when "
                                "its own conversion failed) — download the PDF "
                                "and pass it as a local file for the pdf rung"}
            except Exception:
                return {"status": "fetch_failed",
                        "hint": "both arXiv e-print and ar5iv unreachable"}
    return {"status": "unsupported_input",
            "hint": f"cannot route '{target}' — supported: arXiv id, .tex, .pdf "
                    "(docx/ocr rungs are backlog)"}


def main(argv=None):
    p = argparse.ArgumentParser(prog="paper2pack")
    p.add_argument("target")
    p.add_argument("-o", "--output", default="paper_pack.json")
    a = p.parse_args(argv)
    pack = build_pack(a.target)
    Path(a.output).write_text(json.dumps(pack, ensure_ascii=False, indent=1),
                              encoding="utf-8")
    print(f"{a.output}: path={pack.get('extraction', {}).get('path', pack.get('status'))}")
    return 0 if "status" not in pack else 1


if __name__ == "__main__":
    sys.exit(main())
