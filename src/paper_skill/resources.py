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
from urllib.parse import parse_qs, urlparse

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

_YOUTUBE = re.compile(r"(?:youtube\.com/watch\?|youtu\.be/|youtube\.com/embed/)", re.I)
_OEMBED = "https://www.youtube.com/oembed?format=json&url="

_VIDEO_ID_SHAPE = re.compile(r"^[A-Za-z0-9_-]{11}\Z")


def _youtube_video_id(url: str) -> str | None:
    """Pull the id from its actual structural position, not wherever `v=`
    happens to appear first in the raw string -- a `v=` embedded in an
    unrelated query value (e.g. a `next=` redirect target) must never win,
    since that silently yields a wrong thumbnail rather than degrading to a
    plain link. Returns None for anything that doesn't parse to a plausible
    id, including `/embed/videoseries` -- a playlist, not a single video.
    """
    parts = urlparse(url)
    host = parts.netloc.lower()
    if host == "youtube.com" or host.endswith(".youtube.com"):
        if parts.path == "/watch":
            vid = (parse_qs(parts.query).get("v") or [None])[0]
        elif parts.path.startswith("/embed/"):
            seg = parts.path[len("/embed/"):].split("/", 1)[0]
            vid = None if seg == "videoseries" else seg
        else:
            vid = None
    elif host == "youtu.be":
        vid = parts.path.lstrip("/").split("/", 1)[0] or None
    else:
        vid = None
    return vid if vid and _VIDEO_ID_SHAPE.match(vid) else None


# The three aman.ai papers produced 7 resources between them: papers and code,
# zero `visual`, zero `lecture`, though the type vocabulary offers both. Left to
# itself the model reaches for what a researcher cites, not what a learner
# watches -- and these pages are for learners. The sources were never bad; a
# whole category was simply missing, so the check is on composition rather than
# quality.
EDUCATIONAL_TYPES = frozenset({"visual", "lecture"})


def educational_gap(note: dict | None) -> list[str]:
    """Advisory: does this note give the reader anything to learn *from*?

    Deliberately not part of ``verify_resources``. That one is silent offline
    and blocks a note when it fires; this is deterministic, always applies, and
    must never disqualify a note -- see run_research.
    """
    items = [r for r in (note or {}).get("resources") or [] if isinstance(r, dict)]
    if not items:
        return []                # a note with no resources at all is lint_note's fault to report
    if any(r.get("type") in EDUCATIONAL_TYPES for r in items):
        return []
    return ["every resource here is a paper or an implementation — include at "
            "least one `visual` or `lecture` a learner can actually learn "
            "from (an explainer, an animation, a recorded lecture), only if "
            "you are sure it is real and the url is right"]


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
        # Video is the one type the dead-link check cannot see: youtube answers
        # 200 for any id, serving a "Video unavailable" page, so a real channel
        # with an invented id looks exactly like a real lecture. oEmbed 404s on
        # an id that does not exist. Worth the extra call now that the note is
        # required to carry a lecture -- that requirement is precisely the
        # pressure that invents one.
        if _YOUTUBE.search(url):
            try:
                code = head(_OEMBED + url, timeout=25, allow_redirects=True,
                            headers=UA).status_code
            except Exception:
                continue                 # unreachable checker, not a bad note
            if code in _DEAD_STATUS:
                problems.append(f"{url} is not a real YouTube video")
            continue
        try:
            status = head(url, timeout=25, allow_redirects=True, headers=UA).status_code
        except Exception:
            problems.append(f"{url} is unreachable")
            continue
        if status in _DEAD_STATUS:
            problems.append(f"{url} returns {status}")
    return problems


def embed_kind(url: str, head=requests.head) -> dict:
    """Classify a resource url at build time so the dashboard never has to
    fetch it itself. Deliberately not wired into verify_resources or
    educational_gap -- this is pure classification, called separately by
    whatever renders the resource.

    YouTube needs no probe: the thumbnail is a predictable url derived from
    the video id. Everything else gets one HEAD -- and, same precedent as
    verify_resources treating a 403 as "host refused the probe" rather than
    "dead page", any exception or non-2xx here just falls back to a plain
    link. This function never claims a resource is broken, only that it
    could not confirm it was embeddable.
    """
    if not url or not url.startswith("http"):
        return {"kind": "link"}

    if _YOUTUBE.search(url):
        vid = _youtube_video_id(url)
        if not vid:
            return {"kind": "link"}
        return {"kind": "video",
                "src": f"https://img.youtube.com/vi/{vid}/hqdefault.jpg",
                "href": url}

    try:
        resp = head(url, timeout=25, allow_redirects=True, headers=UA)
    except Exception:
        return {"kind": "link"}
    if not (200 <= resp.status_code < 300):
        return {"kind": "link"}

    content_type = ""
    for key, value in (getattr(resp, "headers", None) or {}).items():
        if key.lower() == "content-type":
            content_type = value or ""
            break
    # "Image/PNG; charset=binary" is still an image -- match the type
    # prefix, not the whole header value.
    if content_type.split(";", 1)[0].strip().lower().startswith("image/"):
        return {"kind": "image", "src": url}
    return {"kind": "link"}
