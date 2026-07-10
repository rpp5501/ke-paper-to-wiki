import io, tarfile
from paper_skill.paper2pack import build_pack, detect

class Resp:
    def __init__(self, content): self.content = content
    def raise_for_status(self): pass


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


def test_no_apis_blocks_download_not_local(tmp_path, monkeypatch):
    monkeypatch.setenv("RESEARCH_MCP_NO_APIS", "1")
    pack = build_pack("1706.03762", get=None, cache_dir=tmp_path)
    assert pack["status"] == "apis_disabled"
    tex = tmp_path / "local.tex"
    tex.write_text(r"\section{A}\begin{equation}x=1\end{equation}")
    local = build_pack(str(tex), get=None, cache_dir=tmp_path)
    assert local["extraction"]["equation_fidelity"] == "exact"
