"""P5 deterministic lint: anchors resolve, claims anchored, links live."""
import os, re, subprocess
from pathlib import Path
import requests

_TIERS = ("{#tldr}", "{#intuition}", "{#mechanics}", "{#the-math}", "{#go-deeper}")
_ANCHOR = re.compile(r"\[(§(sec_[\w]+)|(eq_\d+)|S\d+)\]")
_LINK = re.compile(r"\((https?://[^)]+)\)")


def _head_ok(url: str) -> bool:
    try:
        return requests.head(url, timeout=5, allow_redirects=True).status_code < 400
    except requests.RequestException:
        return False


def _mermaid_ok(block: str) -> bool | None:
    script = Path(__file__).resolve().parents[2] / "scripts" / "mermaid_parse.mjs"
    try:
        r = subprocess.run(["node", str(script)], input=block,
                           capture_output=True, text=True, timeout=30)
        return r.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return None                                   # node absent: skipped


def lint_page(page_md: str, pack: dict, check_links=None,
              check_mermaid=None) -> list[str]:
    check_links = check_links or (
        (lambda url: True) if os.environ.get("RESEARCH_MCP_NO_APIS") == "1"
        else _head_ok)
    check_mermaid = check_mermaid or _mermaid_ok
    probs = []
    for t in _TIERS:
        if t not in page_md:
            probs.append(f"missing tier {t}")
    valid_ids = ({s["id"] for s in pack["sections"]}
                 | {e["id"] for e in pack["equations"]})
    for m in _ANCHOR.finditer(page_md):
        ref = m.group(2) or m.group(3)
        if ref and ref not in valid_ids:
            probs.append(f"dangling anchor: {ref}")
    for tier in ("{#mechanics}", "{#the-math}"):
        if tier not in page_md:
            continue
        body = page_md.split(tier, 1)[1].split("## ", 1)[0]
        for para in (p.strip() for p in body.split("\n\n") if p.strip()):
            if len(para.split()) >= 4 and not _ANCHOR.search(para):
                probs.append(f"unanchored claim in {tier}: {para[:60]}…")
    for m in _LINK.finditer(page_md):
        if not check_links(m.group(1)):
            probs.append(f"dead link: {m.group(1)}")
    for block in re.findall(r"```mermaid\n(.*?)```", page_md, re.S):
        ok = check_mermaid(block)
        if ok is False:
            probs.append("mermaid block fails to parse")
        elif ok is None:
            probs.append("mermaid check skipped (node/mermaid not installed)")
    return probs
