"""Contract tests: round-trip each rung producer's real output through the
pinned paper_pack schema (§ binding global constraint — every successful
pack must validate against src/paper_skill/schemas/paper_pack.schema.json).
"""
import json
from pathlib import Path

import jsonschema

from paper_skill.latex_pack import latex_to_pack
from paper_skill.paper2pack import _pack_from_ar5iv, _pack_from_pdf

SCHEMA = json.loads((Path(__file__).resolve().parents[1] / "src" / "paper_skill" /
                     "schemas" / "paper_pack.schema.json").read_text(encoding="utf-8"))


def test_latex_pack_validates():
    tex = r"""
    \documentclass{article}
    \begin{document}
    \section{Introduction}
    Some intro text.
    \begin{equation}
    E = mc^2
    \end{equation}
    \end{document}
    """
    pack = latex_to_pack(tex, source="arXiv:1706.03762", title="Test Paper")
    jsonschema.validate(pack, SCHEMA)


def test_ar5iv_pack_validates():
    html = (
        b"<html><head><title>Test Paper</title></head><body>"
        b"<h2>Introduction</h2>"
        b'<math alttext="E = mc^2"><mi>E</mi></math>'
        b"</body></html>"
    )
    pack = _pack_from_ar5iv(html, source="arXiv:1706.03762")
    jsonschema.validate(pack, SCHEMA)


def test_pdf_pack_validates(tmp_path):
    import fitz

    p = tmp_path / "sample.pdf"
    d = fitz.open()
    pg = d.new_page()
    pg.insert_text((72, 72), "Body text.")
    d.save(str(p))
    d.close()

    pack = _pack_from_pdf(str(p), source=f"file:{p}")
    jsonschema.validate(pack, SCHEMA)
