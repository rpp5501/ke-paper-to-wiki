"""Deterministic readability checks for generated tutor pages."""
import re


_WORD = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?")
_LIST_ITEM = re.compile(r"^(?:[-+*]|\d+[.)])\s+(?P<content>.+)$")

_FENCE_BLOCK = re.compile(r"```.*?```", re.S)
_DISPLAY_MATH = re.compile(r"\$\$.*?\$\$", re.S)
_MERMAID_FENCE = re.compile(r"^```mermaid\s*$", re.M)
# Prose that walks the reader along edges: LaTeX and ASCII arrows alike.
_ARROW = re.compile(r"\\to\b|\\rightarrow\b|-->|→")
# Relations in a graph. Narrow on purpose: these name a structural relation,
# unlike "node" or "edge", which show up in prose about data structures and
# neural nets. "back-door path" and never bare "backdoor" -- in a security
# paper that word means a planted trojan, and the bare form flagged six pages
# of the backdoor-attack paper for a homonym.
_STRUCTURE_TERM = re.compile(
    r"\b(parent set|adjustment set|back-?door path|collider|v-structure|"
    r"d-separat\w*|descendant|ancestor|directed path|directed cycle|"
    r"acyclic|topological order)\b", re.I)

# How parts connect and in what order, in any field. Without this the check
# was causal-paper-shaped: it scored every page of the Transformer paper zero,
# including the encoder-decoder stack, which is the page most in need of a
# picture in that whole build.
_DATAFLOW_TERM = re.compile(
    r"\b(sub-?layer|residual connection|encoder|decoder|stacked|stack of|"
    r"consists of|composed of|feeds? (?:into|forward)|passes? through|"
    r"followed by|output of (?:each|the)|input to (?:each|the)|"
    r"in parallel|pipeline|propagate\w* through)\b", re.I)

# ponytail: a signal count, not a parse. It asks "does this page walk the
# reader along edges often enough that a picture would carry it better", and
# a page can satisfy it with one diagram however many relations it describes.
# Calibrated against the 24 SID pages (see tests); raise the floor rather than
# widen the vocabulary if a future paper trips it spuriously.
DIAGRAM_SIGNAL_FLOOR = 8

# A page that exists to report what the paper measured, by its own title.
# Matched on the page identity and never on prose: "comparison" and "evaluate"
# are ordinary words, and matching them in body text flagged the SID
# terminology page as an experiment.
# Whole words, because the substring form quietly turned method and theory
# pages into results pages: "variation" fired on variational-lower-bound and
# variational-inference, and "simulation" fired on simulation-based-inference.
# Demanding six numbers from a page whose job is to derive a bound is the same
# causal-paper-shaped error the diagram floor made, in the other direction --
# and none of the four builds on disk happens to contain such a page, which is
# exactly why it survived.
_RESULTS_PAGE = re.compile(
    r"\bresults?\b|\bexperiments?\b|\bexperimental\b|\bablations?\b"
    r"|\bevaluations?\b|\bperformance\b|\bbenchmarks?\b"
    r"|\bsimulations?\b(?!\s*based)|\bvariations\b", re.I)
_FIGURE = re.compile(r"\b\d+(?:\.\d+)?\s*%|\b\d+\.\d+\b|\b\d{2,}\b")

# ponytail: counts figures, does not check they are the right ones -- that is
# the evidence anchor's job. Six is "a couple of conditions with numbers
# against them", calibrated so results pages carrying their table pass and
# ones that only describe the outcome in words do not.
RESULTS_FIGURE_FLOOR = 6


def prose_word_counts(markdown: str) -> list[int]:
    return [words for _text, words in _prose_paragraphs(markdown)]


def _prose_paragraphs(markdown: str) -> list[tuple[str, int]]:
    """Each prose paragraph with its word count.

    The text is carried alongside the count so a problem can quote the
    paragraph it is about; see pedagogy_problems.
    """
    counts: list[tuple[str, int]] = []
    current: list[str] = []
    in_fence = False
    in_equation = False

    def flush() -> None:
        if current:
            joined = " ".join(current)
            counts.append((joined, len(_WORD.findall(joined))))
            current.clear()

    for raw_line in markdown.splitlines() + [""]:
        line = raw_line.strip()
        if line.startswith("```"):
            flush()
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if line.startswith("$$") or (in_equation and "$$" in line):
            flush()
            if line.count("$$") == 1:
                in_equation = not in_equation
            continue
        if in_equation:
            continue
        if not line:
            flush()
            continue
        item = _LIST_ITEM.match(line)
        if raw_line.startswith(("    ", "\t")) and not item:
            flush()
            continue
        if line.startswith("#") or line.startswith("|"):
            flush()
            continue
        if item:
            flush()
            current.append(item.group("content"))
            flush()
            continue
        if line.startswith(">"):
            line = re.sub(r"^(?:>\s?)+", "", line)
        current.append(line)
    return counts


def structural_signals(markdown: str) -> int:
    """How hard this page leans on relationships a reader has to hold in mind.

    Fenced blocks and display math are excluded: an equation carries its own
    structure, and an ```algorithm block is already a walkthrough. What counts
    is prose that describes a shape the reader must assemble from words.
    """
    body = _DISPLAY_MATH.sub(" ", _FENCE_BLOCK.sub(" ", markdown))
    return (len(_ARROW.findall(body))
            + len(_STRUCTURE_TERM.findall(body))
            + len(_DATAFLOW_TERM.findall(body)))


def has_diagram(markdown: str) -> bool:
    return bool(_MERMAID_FENCE.search(markdown))


def is_results_page(page_id: str) -> bool:
    return bool(_RESULTS_PAGE.search((page_id or "").replace("-", " ").replace("_", " ")))


def figure_count(markdown: str) -> int:
    return len(_FIGURE.findall(_FENCE_BLOCK.sub(" ", markdown)))


def _opening(text: str, words: int = 8) -> str:
    return " ".join(text.split()[:words])


def pedagogy_problems(markdown: str, page_id: str = "") -> list[str]:
    paragraphs = _prose_paragraphs(markdown)
    counts = [words for _text, words in paragraphs]
    # Quoted, not just numbered: these strings are the writer's only
    # correction on a retry, and it does not index paragraphs the way this
    # function does. Given a bare ordinal it has to guess which one to cut.
    problems = [
        f"prose paragraph {index} exceeds 100 words ({words}), "
        f"starting {_opening(text)!r}"
        for index, (text, words) in enumerate(paragraphs, start=1) if words > 100
    ]
    over_60 = [text for text, words in paragraphs if words > 60]
    if counts and len(over_60) / len(counts) > 0.10:
        problems.append(
            f"{len(over_60)}/{len(counts)} prose paragraphs exceed 60 words, "
            "starting: " + "; ".join(repr(_opening(t)) for t in over_60))
    signals = structural_signals(markdown)
    if signals >= DIAGRAM_SIGNAL_FLOOR and not has_diagram(markdown):
        problems.append(
            f"describes structure {signals} times with no ```mermaid diagram "
            f"(floor {DIAGRAM_SIGNAL_FLOOR})")
    if is_results_page(page_id):
        figures = figure_count(markdown)
        if figures < RESULTS_FIGURE_FLOOR:
            problems.append(
                f"reports results but carries only {figures} figures "
                f"(floor {RESULTS_FIGURE_FLOOR}) — give the reader the "
                f"numbers, not a description of them")
    return problems
