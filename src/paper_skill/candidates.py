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

import requests

DEFAULT_LIMIT = 6

# research_mcp.search_arxiv hardcodes timeout=30, and arXiv's full-text
# endpoint drifts past that under load: three consecutive searches failed at
# exactly 30.5s, then the same queries answered in 2.9s, 1.0s and 0.9s at 60.
# Losing the most CS-relevant provider on a slow minute is what left the field
# to Crossref and OpenAlex, which index every science and rank 1955 papers on
# amine oxidases above backdoor detection.
PROVIDER_TIMEOUT = 60


def patient_get(url, _get=None, **kwargs):
    """requests.get with a floor under the timeout, for slow-but-working APIs."""
    kwargs["timeout"] = max(kwargs.get("timeout") or 0, PROVIDER_TIMEOUT)
    return (_get or requests.get)(url, **kwargs)


# Ordinary words carry no subject, so they must not count toward relevance.
_STOPWORDS = frozenset("""a an the and or of for to in on with without via from
by as at is are be its it this that these those using use used approach method
methods model models problem scenario setting general new novel towards toward
based between over under into per each other others than then when where why
how what which who whom whose all any both few more most some such no nor not
only own same so too very can will just should now step steps case cases
procedure statistic function functions type types form forms part parts""".split())


def paper_topic(graph: dict, floor: int = 2) -> str:
    """The words that recur across the paper's top-level concepts.

    Used to build the second of find_candidates' two queries, never to replace
    the first: as a prefix it outweighs the concept in every provider's
    ranking. Nothing is returned when nothing recurs, which costs only the
    second search -- better than searching twice for a subject invented out of
    one-off labels.
    """
    words = Counter()
    for node in graph.get("nodes", []):
        if node.get("level") != 1:
            continue
        words.update({w for w in re.findall(r"[a-z]{3,}",
                                            (node.get("label") or "").lower())
                      if w not in _STOPWORDS})
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
    """Candidates for one concept, asked for both ways and merged.

    Measured on both sides. The bare query is what surfaced TABOR for
    "baseline-detectors-nc-tabor" -- the detector the concept is named after --
    while prefixing the paper's subject buried it under generic security
    surveys. For "lagrangian-optimization" the bare query returned the Steiner
    ratio and online strip packing, correct for the words and useless to a
    reader of a backdoor paper, and the prefix is what holds it in the field.
    Neither wins twice, so both are asked; each result set is filtered against
    the query that produced it, and the union is deduplicated by url.
    """
    if search is None:
        from research_mcp import fetch_academic

        def search(q, **kwargs):
            return fetch_academic.academic_search(q, get=patient_get, **kwargs)

    bare = research_query(brief)
    queries = [bare] + ([f"{topic} {bare}"] if topic else [])
    merged: dict[str, dict] = {}
    for query in queries:
        try:
            found = search(query, limit=limit)
        except Exception:
            # Opportunistic: providers being down must not cost a reader a note.
            continue
        for record in relevant((found or {}).get("results") or [], query):
            merged.setdefault(record.get("url") or record.get("title", ""), record)
    return list(merged.values())


def research_query(brief: dict) -> str:
    """The concept and its definition, and deliberately nothing else.

    Prefixing the paper's own subject was tried and measured worse: for
    "lagrangian optimization" a bare query returned Lipschitz bounds and
    large-scale optimization methods, while prefixing "backdoor attack
    detection" drowned it in generic security surveys. Three strong field
    terms outweigh the concept in every provider's ranking. relevant() is
    where field noise gets removed, and it does that job without narrowing
    what was asked for.
    """
    concept = (brief.get("concept") or "").replace("-", " ").replace("_", " ")
    return " ".join(f"{concept} {brief.get('definition', '')}".split())


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
