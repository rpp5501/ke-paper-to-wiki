"""Check that a research note's resources are the things it says they are.

P3 asks the model to recall resources "from your own knowledge", and recall
fails in a way link-checking cannot see: across the four builds on disk, 2 of
15 cited arXiv ids pointed at a completely different paper, and BOTH returned
HTTP 200. A page on backdoor defenses cited a fashion-recommendation paper.

So the identifier is resolved and the title compared, rather than the URL
merely pinged. Everything here is deterministic and injectable -- the network
calls go through ``get``/``head`` so the tests never leave the machine.
"""
import difflib
import os
import re
import xml.etree.ElementTree as ET

import requests

UA = {"User-Agent": "paper-skill/0.1 (keyless research tool)"}
ARXIV_API = "http://export.arxiv.org/api/query"
_ATOM = {"a": "http://www.w3.org/2005/Atom"}
_ARXIV_URL = re.compile(r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})", re.I)

# Compared after normalisation, and only when neither title contains the other,
# so the common "Title (Author et al., 2017)" citation form passes on
# containment and never reaches the ratio. 0.6 separates the two real
# mismatches found in the builds from every correct citation in them.
TITLE_MATCH_FLOOR = 0.6

# A 403 or 405 is the host refusing the probe, not a missing page: publishers
# and university sites routinely block HEAD from an unknown agent. Only an
# answer that means "there is nothing here" counts against the note.
_DEAD_STATUS = {404, 410}


def _no_apis() -> bool:
    return os.environ.get("RESEARCH_MCP_NO_APIS", "") == "1"


def _norm(text: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).split())


def titles_agree(claimed: str, actual: str) -> bool:
    """Does the cited title name the paper the id actually resolves to?"""
    c, a = _norm(claimed), _norm(actual)
    if not c or not a:
        return True                      # nothing to compare -- do not invent a fault
    if a in c or c in a:
        return True
    return difflib.SequenceMatcher(None, c, a).ratio() >= TITLE_MATCH_FLOOR


def arxiv_titles(ids: list[str], get=requests.get) -> dict[str, str]:
    """Real titles for arXiv ids, in one call. Missing ids are simply absent:
    arXiv answers an unknown id with an error entry carrying no usable id."""
    if not ids:
        return {}
    resp = get(ARXIV_API, params={"id_list": ",".join(ids), "max_results": len(ids)},
               timeout=60, headers=UA)
    resp.raise_for_status()
    out = {}
    for entry in ET.fromstring(resp.content).findall("a:entry", _ATOM):
        node = entry.find("a:id", _ATOM)
        title = entry.find("a:title", _ATOM)
        if node is None or title is None:
            continue
        out[node.text.rsplit("/", 1)[-1].split("v")[0]] = " ".join(title.text.split())
    return out


def verify_resources(note: dict, get=requests.get, head=requests.head) -> list[str]:
    """Problems with the note's resources, in lint_note's voice.

    Silent when the API kill switch is set: unverifiable is not the same as
    wrong, and blocking every note when the switch is deliberately on would
    make the pipeline unusable offline.
    """
    items = [r for r in (note or {}).get("resources") or [] if isinstance(r, dict)]
    if not items or _no_apis():
        return []

    cited = {}
    for item in items:
        found = _ARXIV_URL.search(item.get("url", "") or "")
        if found:
            cited.setdefault(found.group(1), item.get("title", ""))
    try:
        real = arxiv_titles(sorted(cited), get=get)
    except Exception as exc:
        # The verifier going down must not read as the note being wrong.
        return [f"could not reach arXiv to verify {len(cited)} citation(s): {exc}"]

    problems = []
    for arxiv_id, claimed in sorted(cited.items()):
        actual = real.get(arxiv_id)
        if actual is None:
            problems.append(f"arXiv:{arxiv_id} does not resolve to a paper")
        elif not titles_agree(claimed, actual):
            problems.append(
                f"arXiv:{arxiv_id} is \"{actual}\", not \"{claimed}\" — "
                f"cite the id that matches the title, or drop the resource")

    for item in items:
        url = item.get("url", "") or ""
        if not url.startswith("http") or _ARXIV_URL.search(url):
            continue
        try:
            status = head(url, timeout=25, allow_redirects=True, headers=UA).status_code
        except Exception:
            problems.append(f"{url} is unreachable")
            continue
        if status in _DEAD_STATUS:
            problems.append(f"{url} returns {status}")
    return problems
