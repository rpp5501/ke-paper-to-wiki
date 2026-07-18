"""P6: pack + graph + pages -> one offline explorer HTML via the fork exporter."""
import argparse
import json
import re
import sys
from pathlib import Path

import markdown


sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "Forked repos" / "graphify"))

_TIER_RE = re.compile(r"^## .+?\{#([\w-]+)\}\s*$", re.M)
_DISPLAY = re.compile(r"\$\$(.+?)\$\$", re.S)
_INLINE = re.compile(r"\\\((.+?)\\\)", re.S)
_LABEL = re.compile(r"\\label\{[^}]*\}")
# Go-Deeper resources are written as prose with a trailing bare URL, not markdown
# link syntax, so python-markdown never autolinks them. Wrap bare URLs (that
# aren't already inside a [text](url) link) in <...> so markdown's own autolink
# rule turns them into clickable <a> tags.
_BARE_URL = re.compile(r"(?<!\]\()https?://[^\s<>\)\]]+")
# Common non-standard macros paper preambles declare via \DeclareMathOperator /
# \newcommand that KaTeX does not ship; expand them so verbatim source math renders.
_KATEX_MACROS = {
    r"\maximize": r"\operatorname*{maximize}", r"\minimize": r"\operatorname*{minimize}",
    r"\argmax": r"\operatorname*{arg\,max}", r"\argmin": r"\operatorname*{arg\,min}",
    r"\mathds": r"\mathbb", r"\bm": r"\boldsymbol",
}


def _sanitize_latex(tex: str) -> str:
    """Make verbatim source LaTeX KaTeX-renderable without changing its meaning:
    drop cross-ref \\label{}, expand common preamble macros, and wrap a bare
    alignment body (has & or \\\\ but no environment) in aligned."""
    tex = _LABEL.sub("", tex).strip()
    for name, repl in _KATEX_MACROS.items():
        tex = tex.replace(name, repl)
    if (("&" in tex) or ("\\\\" in tex)) and "\\begin{" not in tex:
        tex = r"\begin{aligned}" + tex + r"\end{aligned}"
    return tex.strip()


def _autolink_bare_url(match: re.Match) -> str:
    raw = match.group(0)
    url = raw.rstrip(".,;:")
    return f"<{url}>{raw[len(url):]}"


def _mathify(md_text: str) -> str:
    """Stash math as placeholders, run markdown, then restore rendered spans, so
    markdown never mangles LaTeX (e.g. paired underscores becoming <em>)."""
    stash = []

    def _stash(open_d, close_d):
        def repl(m):
            stash.append(f'<span class="math">{open_d}{_sanitize_latex(m.group(1))}'
                         f'{close_d}</span>')
            return f"zzmathstashzz{len(stash) - 1}zzendzz"
        return repl

    md_text = _DISPLAY.sub(_stash("$$", "$$"), md_text)
    md_text = _INLINE.sub(_stash("\\(", "\\)"), md_text)
    md_text = _BARE_URL.sub(_autolink_bare_url, md_text)
    html = markdown.markdown(md_text)
    for i, span in enumerate(stash):
        html = html.replace(f"zzmathstashzz{i}zzendzz", span)
    return html


def split_tiers(page_md: str) -> dict:
    """Convert anchored P4 markdown tiers to HTML keyed by tier anchor."""
    marks = list(_TIER_RE.finditer(page_md))
    tiers = {}
    for index, mark in enumerate(marks):
        end = marks[index + 1].start() if index + 1 < len(marks) else len(page_md)
        body = page_md[mark.end() : end].strip()
        tiers[mark.group(1)] = _mathify(body)
    return tiers


def build_explorer(pack: dict, graph: dict, pages_dir, out_path) -> dict:
    """Build an offline explorer from P4 pages and the concept graph."""
    from graphify.exporters.explorer import to_explorer_html

    pages = {}
    page_names = {}
    for page_file in sorted(Path(pages_dir).glob("*.md")):
        concept_id = page_file.stem.split("_", 1)[1] if "_" in page_file.stem else page_file.stem
        pages[concept_id] = split_tiers(page_file.read_text(encoding="utf-8"))
        page_names[concept_id] = page_file.name
    for node in graph["nodes"]:
        if node["id"] in pages:
            node.setdefault("page", page_names[node["id"]])
            node.setdefault("anchor", "#tldr")
    html = to_explorer_html(graph, title=pack["meta"]["title"], pages=pages)
    Path(out_path).write_text(html, encoding="utf-8")
    return {"status": "ok", "pages": len(pages), "bytes": len(html)}


def main(argv=None):
    parser = argparse.ArgumentParser(prog="p6_explorer")
    parser.add_argument("pack")
    parser.add_argument("graph")
    parser.add_argument("pages")
    parser.add_argument("-o", "--output", default="explorer.html")
    args = parser.parse_args(argv)
    result = build_explorer(
        json.loads(Path(args.pack).read_text(encoding="utf-8")),
        json.loads(Path(args.graph).read_text(encoding="utf-8")),
        args.pages,
        args.output,
    )
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
