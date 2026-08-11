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


# LaTeX writes \includegraphics{Figures/ModalNet-21} without an extension and
# lets the driver pick the file. Ordered by what a reader can be shown without
# conversion, so a paper shipping both a .png and a .pdf gives up the .png.
_GRAPHIC_SUFFIXES = ("", ".png", ".jpg", ".jpeg", ".pdf", ".eps", ".svg")


def _relative(path: str) -> str:
    """Drop a leading ./ so a reference and a tarball member can be compared."""
    return path[2:] if path.startswith("./") else path


# 150 DPI is legible for a figure at page width without turning a 34 KB vector
# into megabytes. block.pdf went the other way entirely: 399.7 KB -> 11.9 KB.
RASTER_DPI = 150


def _rasterise(name: str, data: bytes) -> tuple[str, bytes]:
    """A PDF figure as a PNG, or unchanged if it will not open.

    LaTeX figures are very often PDF -- all 7 of ResNet's and all 13 of DDIM's
    are -- and no browser renders a PDF in an <img>. A figure that cannot be
    rasterised is kept rather than dropped: it is still evidence the figure
    exists, and the dashboard can skip what it cannot show.
    """
    if not name.lower().endswith(".pdf"):
        return name, data
    try:
        import fitz

        with fitz.open(stream=data, filetype="pdf") as doc:
            png = doc[0].get_pixmap(dpi=RASTER_DPI).tobytes("png")
        return name[:-4] + ".png", png
    except Exception:
        return name, data


def extract_assets(blob: bytes, figures: list[dict]) -> dict[str, bytes]:
    """The image bytes each figure's graphics resolve to, keyed by tarball name.

    A caption without its picture is a promise the reader cannot cash, and the
    pictures are already inside the e-print tarball -- 12 for AIAYN, 45 for
    MM-BD -- which the pack builder downloads and then discarded.
    """
    tf = tarfile.open(fileobj=io.BytesIO(blob), mode="r:*")
    members = {_relative(m.name): m for m in tf.getmembers() if m.isfile()}
    assets: dict[str, bytes] = {}
    for figure in figures:
        resolved = []
        for graphic in figure.get("graphics", []):
            # Both sides need normalising, not just the member: AIAYN writes
            # \includegraphics{./vis/anaphora_resolution_new.pdf} against a
            # member stored as vis/anaphora_resolution_new.pdf, and its
            # attention visualisations resolved to nothing.
            ref = _relative(graphic)
            name = next((ref + s for s in _GRAPHIC_SUFFIXES
                         if (ref + s) in members), None)
            if name is None:
                continue
            shown, data = _rasterise(name, tf.extractfile(members[name]).read())
            assets.setdefault(shown, data)
            resolved.append(shown)
        figure["assets"] = resolved
    return assets


def _pack_from_tarball(blob: bytes, source: str) -> dict:
    tf = tarfile.open(fileobj=io.BytesIO(blob), mode="r:*")
    files = {m.name: tf.extractfile(m).read().decode("utf-8", "replace")
             for m in tf.getmembers() if m.isfile()}
    # A .sty is not the paper. Conference style files mention \documentclass
    # (ICLR's and CVPR's both do), and taking the first file that merely
    # CONTAINS the string handed the parser cvpr.sty in place of ResNet and
    # iclr2021_conference.sty in place of DDIM -- 2 and 3 sections, no
    # equations, and "equation_fidelity: exact" stamped on a pack with none of
    # the paper in it. \begin{document} is the discriminator: a class or style
    # file never carries one. _require_content cannot catch this on its own,
    # since a style file does parse to a few sections.
    tex = {n: t for n, t in files.items() if n.lower().endswith(".tex")}
    main = next((t for t in tex.values() if r"\begin{document}" in t),
                next((t for t in tex.values() if "\\documentclass" in t),
                     next((t for t in files.values() if "\\documentclass" in t),
                          next(iter(files.values()), ""))))
    def resolve(name):
        return files.get(name) or files.get(name + ".tex") or ""
    pack = latex_to_pack(main, resolve_input=resolve, source=source)
    bbl = next((t for n, t in files.items() if n.endswith(".bbl")), "")
    if not bbl:
        bbl = next((t for t in files.values() if r"\begin{thebibliography}" in t), "")
    if bbl:
        pack["references"] = parse_bbl(bbl)
    # Mutates each figure to record the file it resolved to; the bytes go back
    # to the caller, which owns where they are written.
    pack["assets"] = extract_assets(blob, pack.get("figures", []))
    return pack


def _pack_from_ar5iv(html: bytes, source: str) -> dict:
    import datetime
    from selectolax.parser import HTMLParser
    doc = HTMLParser(html)
    sections, equations, tables = [], [], []
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
        elif node.tag == "table":
            rows = []
            for tr in node.css("tr"):
                cells = [c.text(strip=True) for c in tr.css("td, th")]
                if any(cells):
                    rows.append(cells)
            if not rows:
                continue
            # ar5iv keeps the caption in a sibling figcaption/caption rather
            # than inside the table, so look at the enclosing figure first.
            caption = ""
            holder = node.parent
            while holder is not None and not caption:
                cap = holder.css_first("figcaption, caption")
                if cap is not None:
                    caption = cap.text(strip=True)
                holder = holder.parent if holder.tag != "body" else None
            tables.append({"id": f"tab_{len(tables) + 1}",
                           "section": current_section,
                           "caption": caption, "rows": rows})
    return {"meta": {"source": source, "title": doc.css_first("title").text()
                     if doc.css_first("title") else "",
                     "generated": datetime.date.today().isoformat()},
            "extraction": {"path": "ar5iv",
                           "equation_fidelity": "converted-mathml",
                           "table_fidelity": "exact"},
            "sections": sections, "equations": equations, "tables": tables,
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
            # PyMuPDF's find_tables was tried against a real 19-page paper: it
            # reported a two-cell "table" made of ordinary sentences, and
            # returned the genuine results grid with whole columns collapsed
            # into one cell ("47.96 54.41 60.15 62.54" as a single value).
            # Numbers that land against the wrong condition are a fabricated
            # result, which is worse than having none, so this path reports
            # that it did not try rather than guessing.
            "extraction": {"path": "pdf", "equation_fidelity": "absent",
                           "table_fidelity": "none"},
            "sections": [{"id": "sec_1", "title": "full-text", "level": 1,
                          "text": " ".join(body.split())}],
            "equations": [], "tables": [], "references": [], "figures": []}


_ARXIV_STAMP = re.compile(r"arXiv[:\s]\s*(\d{4}\.\d{4,5})", re.I)


def _pdf_arxiv_id(path: str) -> str | None:
    """The arXiv id from the PDF's own margin stamp, or None.

    Every arXiv PDF carries it, and it names the paper exactly where a title
    search only guesses. First page only, deliberately: the bibliography of a
    paper cites a dozen other arXiv ids, and picking one of those up would
    silently build a different paper than the one on disk.
    """
    import fitz
    try:
        doc = fitz.open(path)
    except Exception:
        return None
    try:
        first = doc[0].get_text() if doc.page_count else ""
    finally:
        doc.close()
    match = _ARXIV_STAMP.search(first)
    return match.group(1) if match else None


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


def _write_assets(pack: dict, assets_dir) -> dict:
    """Take the image bytes out of the pack, writing them if asked.

    pack.json is a JSON document, so bytes cannot be allowed to survive in it
    -- they would raise at json.dump, at the very end of a long run. The
    figures keep the resolved filenames either way, so a pack inspected
    without an assets_dir still says what it would have written.
    """
    assets = pack.pop("assets", None) or {}
    if not assets_dir:
        return pack
    root = Path(assets_dir)
    for name, blob in assets.items():
        out = root / name
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(blob)
    return pack


def build_pack(target: str, get=requests.get, cache_dir=None,
               assets_dir=None) -> dict:
    kind = detect(target)
    if kind == "tex":
        return latex_to_pack(Path(target).read_text(encoding="utf-8"),
                             source=f"file:{target}")
    if kind == "pdf":
        if not _no_apis():
            # The paper's own stamp first: it names the id outright, where a
            # title search only guesses -- and on an arXiv PDF the stamp IS
            # what _pdf_title returns, so the search was being run on
            # "1306.1043v2" and finding nothing.
            ax = _pdf_arxiv_id(target)
            if not ax:
                from .upgrade import find_arxiv_sibling
                ax = find_arxiv_sibling(_pdf_title(target), get=get)
            if ax:
                upgraded = build_pack(f"arXiv:{ax}", get=get, cache_dir=cache_dir)
                # An id that arXiv cannot serve must not cost the reader the
                # PDF they already have on disk.
                if "sections" in upgraded:
                    return upgraded
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
            return _write_assets(
                _require_content(_pack_from_tarball(resp.content, source)),
                assets_dir)
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
