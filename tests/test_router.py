import io, json, tarfile
from paper_skill.paper2pack import build_pack, detect, _pack_from_ar5iv

class Resp:
    def __init__(self, content): self.content = content
    def raise_for_status(self): pass
    def json(self): return json.loads(self.content)


def _tarball():
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as t:
        tex = (r"\documentclass{article}\begin{document}\section{Intro}"
               r"\begin{equation}E=mc^2\end{equation}\end{document}").encode()
        info = tarfile.TarInfo("main.tex"); info.size = len(tex)
        t.addfile(info, io.BytesIO(tex))
        bbl = (r"\begin{thebibliography}{1}\bibitem{x} Y. arXiv:1409.0473."
               r"\end{thebibliography}").encode()
        info2 = tarfile.TarInfo("main.bbl"); info2.size = len(bbl)
        t.addfile(info2, io.BytesIO(bbl))
    return buf.getvalue()


def test_detect_is_deterministic(tmp_path):
    assert detect("1706.03762") == "arxiv"
    assert detect("arXiv:1706.03762") == "arxiv"
    p = tmp_path / "x.tex"; p.write_text("x")
    assert detect(str(p)) == "tex"
    q = tmp_path / "x.pdf"; q.write_bytes(b"%PDF-1.4")
    assert detect(str(q)) == "pdf"


def test_arxiv_rung1_builds_exact_pack(tmp_path):
    pack = build_pack("1706.03762", get=lambda url, timeout, headers: Resp(_tarball()),
                      cache_dir=tmp_path)
    assert pack["extraction"]["path"] == "latex"
    assert pack["equations"][0]["latex"] == "E=mc^2"
    assert pack["references"][0]["arxiv_id"] == "1409.0473"


def test_tarball_inline_thebibliography_is_parsed():
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as t:
        tex = (r"\documentclass{article}\begin{document}\section{Intro}"
               r"\begin{equation}E=mc^2\end{equation}"
               r"\begin{thebibliography}{2}"
               r"\bibitem{a} Foo. arXiv:1409.0473, 2014."
               r"\bibitem{b} Bar. CVPR 2016."
               r"\end{thebibliography}\end{document}").encode()
        info = tarfile.TarInfo("main.tex"); info.size = len(tex)
        t.addfile(info, io.BytesIO(tex))
    pack = build_pack("1706.03762", get=lambda url, timeout, headers: Resp(buf.getvalue()))
    assert len(pack["references"]) == 2
    assert pack["references"][0]["arxiv_id"] == "1409.0473"


def test_no_apis_blocks_download_not_local(tmp_path, monkeypatch):
    monkeypatch.setenv("RESEARCH_MCP_NO_APIS", "1")
    pack = build_pack("1706.03762", get=None, cache_dir=tmp_path)
    assert pack["status"] == "apis_disabled"
    tex = tmp_path / "local.tex"
    tex.write_text(r"\section{A}\begin{equation}x=1\end{equation}")
    local = build_pack(str(tex), get=None, cache_dir=tmp_path)
    assert local["extraction"]["equation_fidelity"] == "exact"


def test_ar5iv_fallback_anchors_equations_to_their_section():
    html = (
        b"<html><head><title>T</title></head><body>"
        b"<h2>Section A</h2>"
        b'<math alttext="a=1"></math>'
        b"<h2>Section B</h2>"
        b'<math alttext="b=2"></math>'
        b"</body></html>"
    )
    pack = _pack_from_ar5iv(html, source="arXiv:1706.03762")
    assert pack["extraction"] == {"path": "ar5iv", "equation_fidelity": "converted-mathml"}
    sec_a = pack["sections"][0]["id"]
    sec_b = pack["sections"][1]["id"]
    eq_a = next(e for e in pack["equations"] if e["latex"] == "a=1")
    eq_b = next(e for e in pack["equations"] if e["latex"] == "b=2")
    assert eq_a["section"] == sec_a
    assert eq_b["section"] == sec_b
    assert eq_b["section"] != sec_a


def test_ar5iv_equations_are_normalized_too():
    """alttext IS the original LaTeX, so it carries the same \\label and
    orphaned-alignment hazards the tarball rung does. A reader on the ar5iv
    rung sees the same raw-LaTeX fallback if only rung 1 is normalized."""
    html = (b"<html><head><title>T</title></head><body><h2>A</h2>"
            b'<math alttext="\\label{eq:x}a &amp;= 1 \\\\ b &amp;= 2"></math>'
            b"</body></html>")
    latex = _pack_from_ar5iv(html, source="arXiv:1")["equations"][0]["latex"]
    assert r"\label" not in latex
    assert latex.startswith(r"\begin{aligned}")


def test_arxiv_total_failure_is_success_shaped():
    def get(url, timeout, headers):
        raise RuntimeError("network down")
    pack = build_pack("1706.03762", get=get)
    assert pack["status"] == "fetch_failed"


def test_pdf_rung_extracts_text(tmp_path, monkeypatch):
    monkeypatch.setenv("RESEARCH_MCP_NO_APIS", "1")
    import fitz
    p = tmp_path / "sample.pdf"
    d = fitz.open()
    pg = d.new_page()
    pg.insert_text((72, 72), "Hello world sample body.")
    d.save(str(p))
    d.close()
    pack = build_pack(str(p))
    assert pack["extraction"] == {"path": "pdf", "equation_fidelity": "absent"}
    assert pack["sections"][0]["id"] == "sec_1"
    assert "Hello world sample body." in pack["sections"][0]["text"]
    assert pack["equations"] == []


def test_pdf_climbs_to_latex_when_arxiv_sibling_found(tmp_path):
    import fitz
    p = tmp_path / "sample.pdf"
    d = fitz.open()
    pg = d.new_page()
    pg.insert_text((72, 72), "Attention Is All You Need")
    d.save(str(p))
    d.close()

    def get(url, timeout=None, headers=None, params=None):
        if "openalex" in url:
            return Resp(json.dumps(
                {"results": [{"ids": {"arxiv": "https://arxiv.org/abs/1706.03762"}}]}
            ).encode())
        return Resp(_tarball())

    pack = build_pack(str(p), get=get)
    assert pack["extraction"]["path"] == "latex"
    assert pack["equations"][0]["latex"] == "E=mc^2"


def test_pdf_stays_rung4_when_no_sibling(tmp_path):
    import fitz
    p = tmp_path / "sample.pdf"
    d = fitz.open()
    pg = d.new_page()
    pg.insert_text((72, 72), "Some Obscure Unmatched Paper Title")
    d.save(str(p))
    d.close()

    def get(url, timeout=None, headers=None, params=None):
        return Resp(json.dumps({"results": []}).encode())

    pack = build_pack(str(p), get=get)
    assert pack["extraction"] == {"path": "pdf", "equation_fidelity": "absent"}


def test_pdf_no_apis_skips_upgrade(tmp_path, monkeypatch):
    monkeypatch.setenv("RESEARCH_MCP_NO_APIS", "1")
    import fitz
    p = tmp_path / "sample.pdf"
    d = fitz.open()
    pg = d.new_page()
    pg.insert_text((72, 72), "Hello world sample body.")
    d.save(str(p))
    d.close()

    pack = build_pack(str(p), get=None)
    assert pack["extraction"]["path"] == "pdf"


# The fidelity ladder only ever descended on a thrown exception, so a tarball
# that PARSED but yielded nothing was returned as a successful rung-1 pack.
# Measured on arXiv:1412.6980 (Adam): 0 sections, 0 equations, 0 macros, empty
# title -- and paper2pack still reported path=latex. Downstream, P2 would have
# had nothing to extract concepts from, which is exactly the TOC-shaped garbage
# the anti-TOC guard exists to catch, arriving one stage earlier.
def _empty_tarball():
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as t:
        tex = rb"\documentclass{article}\begin{document}\end{document}"
        info = tarfile.TarInfo("main.tex"); info.size = len(tex)
        t.addfile(info, io.BytesIO(tex))
    return buf.getvalue()


AR5IV_HTML = (b"<html><body><h2>1 Introduction</h2><p>Real body text.</p>"
              b"</body></html>")


def test_an_empty_rung1_parse_descends_to_ar5iv():
    calls = []

    def get(url, timeout, headers):
        calls.append(url)
        return Resp(_empty_tarball() if "e-print" in url else AR5IV_HTML)

    pack = build_pack("1412.6980", get=get)
    assert any("ar5iv" in u for u in calls), "ladder never descended"
    assert pack["extraction"]["path"] != "latex"


def test_every_rung_coming_up_empty_is_success_shaped_not_an_empty_pack():
    """ar5iv serves an 8 KB "Untitled Document" stub for arXiv:1412.6980 -- the
    conversion failed upstream, so there is genuinely nothing to extract. The
    pipeline must be told that, not handed a pack with no sections in it."""
    def get(url, timeout, headers):
        return Resp(_empty_tarball() if "e-print" in url
                    else b"<html><body><title>Untitled</title></body></html>")

    pack = build_pack("1412.6980", get=get)
    assert pack.get("status") == "empty_extraction"
    assert "sections" not in pack


def test_a_nonempty_rung1_parse_still_wins():
    """The guard must not make every paper take the slow rung."""
    pack = build_pack("1706.03762", get=lambda url, timeout, headers: Resp(_tarball()))
    assert pack["extraction"]["path"] == "latex"
