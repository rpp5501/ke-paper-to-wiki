"""Real search results for a research brief, instead of recalled ones.

research_mcp.academic_search federates arXiv, Semantic Scholar, OpenAlex and
Crossref and has been sitting next to P3 unused, while P3 asked the model to
remember urls. Offered, never mandated: academic search cannot return the
Illustrated Transformer or the Annotated Transformer, and those are the best
resources in the current builds. verify_resources stays the backstop for
anything cited from outside this list.
"""
import re
from collections import Counter

DEFAULT_LIMIT = 6

# Ordinary words carry no field, so they must not count as a recurring theme.
_STOPWORDS = frozenset("""a an the and or of for to in on with without via from
by as at is are be its it this that these those using use used approach method
methods model models problem scenario setting general new novel towards toward
based between over under into per each other others than then when where why
how what which who whom whose all any both few more most some such no nor not
only own same so too very can will just should now step steps case cases
procedure statistic function functions type types form forms part parts""".split())


def paper_topic(graph: dict, floor: int = 2) -> str:
    """The words that recur across the paper's top-level concepts.

    A concept slug is paper-internal shorthand -- "nc", "tabor", "ba" -- and
    names no field, so searching it bare returned 1950s biochemistry for a
    backdoor-detection concept. What the top-level concepts keep repeating is
    what the paper is about. Nothing is returned when nothing recurs: inventing
    a topic out of one-off labels would poison every query for that paper.
    """
    words = Counter()
    for node in graph.get("nodes", []):
        if node.get("level") != 1:
            continue
        seen = {w for w in re.findall(r"[a-z]{3,}", (node.get("label") or "").lower())
                if w not in _STOPWORDS}
        words.update(seen)
    return " ".join(w for w, n in words.most_common(3) if n >= floor)


# Crude on purpose: "mitigating"/"mitigation" and "detectors"/"detection" are
# the same subject, and exact matching dropped Neural Cleanse from a query
# about mitigation -- the one paper that concept most needed. A real stemmer
# would be a dependency for four suffixes.
# Order matters, and "ion" beats "ation": stripping "ation" sends mitigation to
# "mitig" while mitigating goes to "mitigat", and the two stop matching. Via
# "ion" both land on "mitigat", and detection meets detectors at "detect".
_SUFFIXES = ("ings", "ing", "ions", "ion", "ors", "or", "ers", "er", "es", "s")


def _stem(word: str) -> str:
    for suffix in _SUFFIXES:
        if word.endswith(suffix) and len(word) - len(suffix) >= 4:
            return word[:-len(suffix)]
    return word


def _terms(text: str) -> set:
    return {_stem(w) for w in re.findall(r"[a-z]{3,}", (text or "").lower())
            if w not in _STOPWORDS}


# Crossref gives a paper's tables and figures their own DOIs, so they come back
# from search looking like publications. They overlap the query on wording --
# "Table 2: Performance comparison ... with baseline methods" -- which is
# exactly why the word filter cannot be what excludes them.
_NOT_A_PAPER = re.compile(r"^\s*(table|figure|fig\.?|appendix|supplement\w*)\b"
                          r"\s*[\divx]*\s*[.:—-]", re.I)

# IEEE registers a paper's multimedia supplement under the paper's own DOI with
# an /mmN suffix, so it carries the paper's exact title and only the url tells
# them apart.
_SUPPLEMENT_DOI = re.compile(r"/mm\d+/?$", re.I)

RELEVANCE_FLOOR = 2


def relevant(records: list[dict], query: str,
             floor: int = RELEVANCE_FLOOR) -> list[dict]:
    """Drop results that share no subject with the query.

    academic_search ranks by raw citation count across every field Crossref and
    OpenAlex index, so a 1955 paper on amine oxidases (35 citations) outranked
    the backdoor-detection work actually being asked about (2 citations). Order
    is preserved: this only removes, it does not re-rank.
    """
    wanted = _terms(query)
    # A query with fewer distinctive terms than the floor can never clear it,
    # so filtering on it would return nothing however good the results were.
    # Search that appears to run and find nothing is the exact failure this
    # module exists to remove; hand them on and let the model and
    # verify_resources judge instead.
    if len(wanted) < floor:
        return list(records)
    return [r for r in records
            if not _NOT_A_PAPER.match(r.get("title") or "")
            and not _SUPPLEMENT_DOI.search(r.get("url") or "")
            and len(_terms(r.get("title")) & wanted) >= floor]


def find_candidates(brief: dict, search=None, limit: int = DEFAULT_LIMIT,
                    topic: str = "") -> list[dict]:
    if search is None:
        from research_mcp.fetch_academic import academic_search
        search = academic_search
    query = research_query(brief, topic)
    try:
        found = search(query, limit=limit)
    except Exception:
        # Opportunistic: providers being down must not cost the reader a note.
        return []
    return relevant((found or {}).get("results") or [], query)


def research_query(brief: dict, topic: str = "") -> str:
    concept = (brief.get("concept") or "").replace("-", " ").replace("_", " ")
    return " ".join(f"{topic} {concept} {brief.get('definition', '')}".split())


def candidate_block(records: list[dict]) -> str:
    """Title and url on one line, because splitting them is the actual defect:
    recall paired a real title with a real id belonging to a different paper."""
    if not records:
        return ""
    lines = []
    for r in records:
        year = f" ({r['year']})" if r.get("year") else ""
        cites = f" [{r['citations']} citations]" if r.get("citations") else ""
        lines.append(f"- {r.get('title', '')}{year}{cites}\n  {r.get('url', '')}")
    return "\n".join(lines)
