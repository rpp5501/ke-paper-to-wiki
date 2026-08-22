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
import time
import xml.etree.ElementTree as ET
from urllib.parse import parse_qs, urljoin, urlparse

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

# arXiv rate-limits, and enrichment now verifies ten-plus notes per paper in
# quick succession. Three attempts at 3s/6s covers the 429s seen in practice
# without stalling a build on an arXiv that is genuinely down.
ARXIV_ATTEMPTS = 3
ARXIV_BACKOFF_SECONDS = 3.0

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


def arxiv_titles(ids: list[str], get=requests.get, sleep=time.sleep) -> dict[str, str]:
    """Real titles for arXiv ids, in one call. Missing ids are simply absent:
    arXiv answers an unknown id with an error entry carrying no usable id.

    Retried with backoff because enrichment took P3 from about one concept per
    paper to ten or more, and lottery-ticket then lost four notes to 429 Too
    Many Requests and 503. The note was fine; we asked arXiv too fast. Bounded,
    so a genuinely unreachable arXiv still reports itself rather than hanging.
    """
    if not ids:
        return {}
    for attempt in range(ARXIV_ATTEMPTS):
        try:
            resp = get(ARXIV_API,
                       params={"id_list": ",".join(ids), "max_results": len(ids)},
                       timeout=60, headers=UA)
            resp.raise_for_status()
            break
        except Exception:
            if attempt == ARXIV_ATTEMPTS - 1:
                raise
            sleep(ARXIV_BACKOFF_SECONDS * (2 ** attempt))
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


# Attribute order varies (`property` before or after `content`, name= instead
# of property=), so both orders are matched rather than assuming one. A parser
# would be more correct on pathological markup; this is one meta tag on pages
# that already care about their social preview, and selectolax is only an
# optional dependency here.
_OG_IMAGE = re.compile(
    r"""<meta[^>]+?(?:property|name)\s*=\s*["']og:image(?::url)?["'][^>]*?"""
    r"""content\s*=\s*["']([^"']+)["']"""
    r"""|<meta[^>]+?content\s*=\s*["']([^"']+)["'][^>]*?"""
    r"""(?:property|name)\s*=\s*["']og:image(?::url)?["']""",
    re.I | re.S)

# One page is enough to reach the <head>; a long article body is pure cost.
_PREVIEW_BYTES = 200_000

# Hosts whose og:image is generated per-site, not per-article. Probing the 27
# real `visual` urls in the built papers, arxiv.org returned its own logo and
# paperswithcode.com returned a Hugging Face "trending papers" thumbnail --
# neither shows the reader anything about the concept, while occupying the
# space a diagram would. github.com's card is auto-rendered repo metadata:
# legible, but it is text about the repo, not a picture of the idea. A generic
# card is worse than the plain link it replaces, because it makes a promise.
_GENERIC_CARD_HOSTS = frozenset({
    "arxiv.org", "paperswithcode.com", "github.com", "doi.org",
    "openreview.net", "semanticscholar.org", "huggingface.co",
})


def embed_kind(url: str, head=requests.head, get=requests.get,
               want_preview: bool = False) -> dict:
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

    # A `visual` resource is an explainer -- distill.pub, Jay Alammar, an
    # author's own post -- not an image file, so the check above never fires
    # for one and the reader gets a line of blue text where a diagram was
    # promised. These hosts publish an og:image; borrowing it gives the
    # renderer the preview card it already knows how to draw, still linking
    # through to the page. Opt-in: a social card on every follow-up paper
    # would be noise, and this costs one GET per resource.
    if want_preview and not _has_generic_card(url):
        src = _og_image(url, get)
        # The tag is a claim, not a guarantee: jacobgil.github.io advertises
        # its own site root as its og:image, which would reach the reader as
        # a broken <img>. Confirm it before promoting.
        if src and _is_image(src, head):
            return {"kind": "image", "src": src}
    return {"kind": "link"}


_IMAGE_SUFFIX = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp")


def _is_image(src: str, head) -> bool:
    """Is this og:image url actually an image?

    Same precedent as the probe above treating a 403 as "the host refused"
    rather than "nothing is there": Wikipedia answered 429 and Meta's CDN 403
    for images that load fine in a browser, so a refusal falls back to the
    url's own shape. A 404 is real evidence and overrides the extension --
    cs.umd.edu advertises an img/logo.png that is simply not there.
    """
    looks_like_one = urlparse(src).path.lower().endswith(_IMAGE_SUFFIX)
    try:
        resp = head(src, timeout=25, allow_redirects=True, headers=UA)
    except Exception:
        return looks_like_one
    if resp.status_code in _DEAD_STATUS:
        return False
    content_type = ""
    for key, value in (getattr(resp, "headers", None) or {}).items():
        if key.lower() == "content-type":
            content_type = value or ""
            break
    if content_type.split(";", 1)[0].strip().lower().startswith("image/"):
        return True
    return looks_like_one and not (200 <= resp.status_code < 300)


def _has_generic_card(url: str) -> bool:
    host = urlparse(url).netloc.lower().split(":")[0]
    host = host[4:] if host.startswith("www.") else host
    return any(host == h or host.endswith("." + h) for h in _GENERIC_CARD_HOSTS)


def _og_image(url: str, get) -> str | None:
    """The page's own social-preview image, absolutised against the page.

    Never raises: same precedent as the HEAD path above, a resource that
    cannot be previewed degrades to a plain link rather than failing a build.
    """
    try:
        resp = get(url, timeout=25, allow_redirects=True, headers=UA)
        if not (200 <= resp.status_code < 300):
            return None
        match = _OG_IMAGE.search((resp.text or "")[:_PREVIEW_BYTES])
    except Exception:
        return None
    if not match:
        return None
    src = (match.group(1) or match.group(2) or "").strip()
    if not src:
        return None
    # Pages ship "/img/card.png" and "//cdn/card.png". Handed to an <img> in
    # the dashboard those resolve against the dashboard's own origin and 404.
    src = urljoin(url, src)
    # distill.pub serves over https and writes its og:image tag as http. A
    # browser blocks that as mixed content and the card renders blank -- the
    # exact failure this feature exists to avoid. The page itself proved https
    # works for this host, so the asset is upgraded to match; if the upgraded
    # url does not answer, _is_image declines it and it stays a link.
    if url.startswith("https://") and src.startswith("http://"):
        src = "https://" + src[len("http://"):]
    return src
