"""P5 deterministic lint: anchors resolve, claims anchored, links live."""
import os, re, subprocess
from pathlib import Path
import requests

_TIERS = ("{#tldr}", "{#intuition}", "{#mechanics}", "{#the-math}", "{#go-deeper}")
# tab_N and fig_N belong here with the rest: p4_context offers both to the
# writer as evidence and the contract asks results pages to reproduce the
# paper's numbers and to cite its figures. Without them a paragraph citing a
# table read as an unanchored claim -- noise while lint only wrote a report,
# blocking once the write gate started running it.
_ANCHOR = re.compile(r"\[(§(sec_[\w]+)|((?:eq|tab|fig)_\d+)|S\d+)\]")
# A page written with repo_dir cites the implementation as well as the paper.
# The anchor rule is about traceability, and [sid.py:L24] is traceable; it is
# simply not a pack id, so it satisfies "is anchored" without being subject to
# the dangling-id check above it.
_CODE_REF = re.compile(r"\[[\w./-]+\.(?:py|ts|tsx|js|rs|go|java|cpp|c|h)"
                       r"(?::L?\d+(?:-L?\d+)?)?\]")
_LINK = re.compile(r"\((https?://[^)]+)\)")
_DISPLAY_MATH = re.compile(r"\$\$.*?\$\$", re.S)
_FENCED_BLOCK = re.compile(
    r"^```(?:annotated-eq|derivation|algorithm|figure)\n.*?\n```$", re.S | re.M)

# No formatting check lives here, on purpose. A paragraph ceiling was tried and
# removed: every lint problem is blocking (scripts/gate_slice7.py gates on "all
# pages lint clean"), which turns a style preference into a build failure and
# takes the formatting judgement away from the writer that can see the content.
# Length, bullets and tables are steered by PAGE_PROMPT instead.

# p4_write forbids a tier whose content is that it has no content. A prompt
# rule is a hope; this is the check. Deliberately narrow -- each pattern needs
# an absence word ("no", "not", "lacks", "cannot") next to a context/equation
# word, so ordinary maths prose that merely mentions an equation is untouched.
_NO_CONTENT = (
    # "relevant" belongs here with the rest: a zero-equation paper is normal,
    # and the contract names "no display equation is relevant here" as a
    # checked failure, so the check has to catch it or the rule is advice.
    re.compile(r"\bno\b[^.]{0,60}\bequations?\b[^.]{0,60}"
               r"\b(suppl|present|available|provid|includ|given|tagged|relevan)",
               re.I),
    re.compile(r"\blocal context\b[^.]{0,60}"
               r"\b(does not|lacks|has no|contains no|no )", re.I),
    re.compile(r"\b(cannot|can not|could not|no)\b[^.]{0,60}"
               r"\b(reproduc|render|deriv|express)[^.]{0,60}\bhere\b", re.I),
)


def _fold_multiline(body: str) -> str:
    """Make each $$...$$ block and fenced content block one paragraph.

    p4_write requires equations be reproduced VERBATIM from the pack, and real
    paper LaTeX puts blank lines inside align/array blocks. Splitting on blank
    lines therefore tore one equation into two "paragraphs" and reported the
    half without the trailing [eq_N] anchor as an unanchored claim. Collapsing
    blank lines *inside* the delimiters keeps the block whole with its anchor;
    a block that genuinely has no anchor is still caught.

    Fenced YAML content blocks carry blank lines for exactly the same reason
    and tear the same way.

    A colon lead-in tears the same way from the other side. "The
    identity-shortcut form of the block is:" followed by an anchored equation
    is one thought whose evidence sits on the block, but the blank line between
    them made the lead-in its own anchor-less paragraph. That was the largest
    single cause of failure in the resnet run, and it hit every "here are the
    numbers:" introducing a table too. A lead-in whose block cites nothing is
    still caught, because the merged paragraph then has no anchor either.
    """
    collapse = lambda m: re.sub(r"\n\s*\n", "\n", m.group(0))
    return _FENCED_BLOCK.sub(collapse, _DISPLAY_MATH.sub(collapse, body))


def _paragraphs(body: str) -> list[str]:
    """Tier body split into claim-bearing paragraphs.

    A paragraph ending in a colon introduces the block after it, and the two
    are one thought whose evidence sits on the block -- so they are joined.
    Only when the lead-in carries no anchor itself: the join exists to rescue a
    lead-in with no evidence of its own, and merging one that is already
    anchored would instead hide an unanchored block behind it.
    """
    out: list[str] = []
    for para in (p.strip() for p in body.split("\n\n") if p.strip()):
        if out and out[-1].rstrip("*").endswith(":") and not _ANCHOR.search(out[-1]):
            out[-1] = f"{out[-1]} {para}"
        else:
            out.append(para)
    return out


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
    except (OSError, subprocess.TimeoutExpired):
        return None                                   # node absent: skipped
    if r.returncode == 2:
        return None                                   # mermaid package not installed: skipped
    return r.returncode == 0


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
                 | {e["id"] for e in pack["equations"]}
                 # .get: packs built before table/figure extraction have
                 # neither key, and an old pack must still lint.
                 | {t["id"] for t in pack.get("tables", [])}
                 | {f["id"] for f in pack.get("figures", [])})
    for m in _ANCHOR.finditer(page_md):
        ref = m.group(2) or m.group(3)
        if ref and ref not in valid_ids:
            probs.append(f"dangling anchor: {ref}")
    for tier in ("{#mechanics}", "{#the-math}"):
        if tier not in page_md:
            continue
        body = _fold_multiline(page_md.split(tier, 1)[1].split("## ", 1)[0])
        for para in _paragraphs(body):
            if (len(para.split()) >= 4 and not _ANCHOR.search(para)
                    and not _CODE_REF.search(para)):
                probs.append(f"unanchored claim in {tier}: {para[:60]}…")
            if any(p.search(para) for p in _NO_CONTENT):
                probs.append(
                    f"no-content filler in {tier}: {para[:60]}… — a tier owes "
                    "the reader real material (worked example, complexity or "
                    "termination argument, invariant, boundary case), not a "
                    "report that it has none")
    for m in _LINK.finditer(page_md):
        if not check_links(m.group(1)):
            probs.append(f"dead link: {m.group(1)}")
    for block in re.findall(r"```mermaid\n(.*?)```", page_md, re.S):
        ok = check_mermaid(block)
        if ok is False:
            probs.append("mermaid block fails to parse")
        # ok is None -> skipped (node or the mermaid package unavailable); not
        # a problem, per the plan's own "skipped, not pass" offline-lint rule.
    return probs
