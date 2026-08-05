"""Harvest the paper's shared vocabulary from finished pages, then define it.

Two stages, deliberately split. The harvest is deterministic and free, so a
default build stays byte-identical; only the definitions cost tokens, and only
when asked for. Together they fill the paper-wide `_paper` glossary note, which
build_data already merges into every concept's hover map.

Runtime lookup would have cost offline, keyless, and backend-free all at once.
It does not need to: the terms ARE the words in the finished pages, so the same
call can happen once, here, and ship inside the bundle.
"""
import argparse
import re
from pathlib import Path

import yaml

from .llm_spawn import LLMUnavailable, claude_spawn, parse_json_reply

# Everything that is not prose. Display math must go FIRST: a $...$ pattern
# matches the empty span between the two dollars of $$...$$ and leaves the body
# exposed, which is how \HH and \CC were harvested as terms of art. Headings and
# fenced blocks are the page's own scaffolding, identical on all 24 pages, so
# left in they outscore every real term in the paper.
_NOT_PROSE = (
    re.compile(r"```.*?```", re.S),
    re.compile(r"\$\$.*?\$\$", re.S),
    re.compile(r"\$[^$]*\$"),
    re.compile(r"^#{1,6} .*$", re.M),
    re.compile(r"\{#[\w-]+\}"),
    re.compile(r"\((https?://[^)]+)\)"),
)
# An acronym (CPDAG, SHD) or a hyphenated lowercase compound (d-separation).
# Deliberately only these two: they are the shapes that produced unambiguous
# terms on the papers measured. A capitalised-phrase rule is easy to add if a
# harvest comes back thin, and harder to remove once it starts pulling in
# sentence-initial words and proper nouns.
_CANDIDATE = re.compile(r"\b[A-Z]{2,6}\b|\b[a-z]+(?:-[a-z]+)+\b")

MIN_PAGES = 2

DEFINE_PROMPT = """Define each term for a reader of this paper. Output ONLY a
JSON object mapping each term EXACTLY as given to a one- or two-sentence
definition. No markdown, no commentary.

OMIT any candidate that is not a term of art — ordinary English compounds
("ground-truth", "data-generating", "re-deriving"), section names, and author
initials are noise from a deliberately generous scan. Omitting is expected and
costs nothing; defining a non-term puts a hover on a word nobody needs.

Ground every definition in the page text below. If the pages do not support a
definition, give the term's plain meaning in this paper's context and nothing
more -- never invent a claim the paper does not make. Say what the term is,
then what it is doing here.

TERMS AND WHERE THEY ARE USED:
{evidence}
"""

# Enough to see how a term is used, not so much that the paper is re-sent. The
# whole corpus was being pasted in for every call: 24 pages for a list of terms
# whose evidence is a sentence each.
SNIPPETS_PER_TERM = 3
SNIPPET_CHARS = 240


def _evidence(terms, pages) -> str:
    """Each term with the few places it actually appears."""
    out = []
    for term in terms:
        found = []
        for page in pages:
            start = 0
            while len(found) < SNIPPETS_PER_TERM:
                at = page.find(term, start)
                if at < 0:
                    break
                lo = max(0, at - SNIPPET_CHARS // 2)
                found.append(" ".join(
                    page[lo:at + SNIPPET_CHARS // 2].split()))
                start = at + len(term)
            if len(found) >= SNIPPETS_PER_TERM:
                break
        out.append(f"- {term}\n" + "\n".join(f"    …{s}…" for s in found))
    return "\n".join(out)


def harvest_terms(pages, known) -> list[str]:
    """Terms appearing in MIN_PAGES or more pages and not already defined.

    Ordered by page count, then alphabetically, so two runs over the same
    pages produce the same list.
    """
    counts: dict[str, int] = {}
    for page in pages:
        prose = page
        for pattern in _NOT_PROSE:
            prose = pattern.sub(" ", prose)
        for term in {m.group(0) for m in _CANDIDATE.finditer(prose)}:
            counts[term] = counts.get(term, 0) + 1
    hits = [t for t, n in counts.items() if n >= MIN_PAGES and t not in known]
    return sorted(hits, key=lambda t: (-counts[t], t))


def define_terms(terms, pages, spawn=claude_spawn) -> dict[str, str]:
    """One batched call for the whole list; loud on an unusable reply."""
    if not terms:
        return {}
    reply = spawn(DEFINE_PROMPT.format(evidence=_evidence(terms, pages)))
    parsed = parse_json_reply(reply)
    if not parsed:
        raise LLMUnavailable(
            "term definitions: reply was not a JSON object — "
            f"got {(reply or '')[:200]!r}")
    return {t: str(parsed[t]) for t in terms if t in parsed}


def main(argv=None):
    p = argparse.ArgumentParser(prog="paper_skill.terms")
    p.add_argument("pages_dir")
    p.add_argument("--glossary", required=True,
                   help="wiki/_paper.yaml to merge the definitions into")
    a = p.parse_args(argv)

    pages = [f.read_text(encoding="utf-8")
             for f in sorted(Path(a.pages_dir).glob("*.md"))]
    note_path = Path(a.glossary)
    note = (yaml.safe_load(note_path.read_text(encoding="utf-8"))
            if note_path.exists() else None) or {}
    glossary = note.get("glossary") or {}

    terms = harvest_terms(pages, known=set(glossary))
    print(f"harvested {len(terms)} new terms from {len(pages)} pages")
    if not terms:
        return 0
    glossary.update(define_terms(terms, pages))

    note.setdefault("concept", "_paper")
    note.setdefault("status", "verified")
    note.setdefault("synthesis", "Paper-wide terminology.")
    note["glossary"] = glossary
    note_path.parent.mkdir(parents=True, exist_ok=True)
    note_path.write_text(yaml.safe_dump(note, allow_unicode=True, sort_keys=False),
                         encoding="utf-8")
    print(f"{note_path}: {len(glossary)} terms")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
