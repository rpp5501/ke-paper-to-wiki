"""Deterministic readability checks for generated tutor pages."""
import re


_WORD = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?")
_LIST_ITEM = re.compile(r"^(?:[-+*]|\d+[.)])\s+(?P<content>.+)$")


def prose_word_counts(markdown: str) -> list[int]:
    counts: list[int] = []
    current: list[str] = []
    in_fence = False
    in_equation = False

    def flush() -> None:
        if current:
            counts.append(len(_WORD.findall(" ".join(current))))
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


def pedagogy_problems(markdown: str) -> list[str]:
    counts = prose_word_counts(markdown)
    problems = [
        f"prose paragraph {index} exceeds 100 words ({words})"
        for index, words in enumerate(counts, start=1) if words > 100
    ]
    long_count = sum(words > 60 for words in counts)
    if counts and long_count / len(counts) > 0.10:
        problems.append(
            f"{long_count}/{len(counts)} prose paragraphs exceed 60 words")
    return problems
