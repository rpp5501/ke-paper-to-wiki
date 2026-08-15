"""P4 writers: one spawn per concept page, tier template enforced."""
from pathlib import Path
from research_mcp.inbox import inbox_add
from research_mcp.wiki import wiki_get
from .p4_context import assemble_context
from .pedagogy import pedagogy_problems

TIERS = ("{#tldr}", "{#intuition}", "{#mechanics}", "{#the-math}", "{#go-deeper}")

# Two was the right budget while a "retry" re-sent the identical prompt: extra
# re-rolls of the same dice only cost money. Now that the rejection is fed back
# (see _render_page_prompt), an attempt is a correction and the third one earns
# its keep -- shortening paragraphs can itself push a page over the diagram
# floor, which is a problem the writer only learns about on the round after.
MAX_WRITE_ATTEMPTS = 3

# The dashboard's contentBlocks parser is pinned to this same file by
# contentBlocks.promptFixture.test.ts, so the syntax the writer is shown and the
# syntax the reader's renderer accepts cannot drift apart.
BLOCK_SYNTAX = (Path(__file__).resolve().parents[2] / "dashboard" / "src"
                / "lib" / "contentBlocksExample.md").read_text(encoding="utf-8")

WRITING_SKILL_PATH = (Path(__file__).resolve().parents[2] / "skills"
                      / "write-paper-tutor" / "SKILL.md")
WRITING_SKILL = WRITING_SKILL_PATH.read_text(encoding="utf-8")

_LEGACY_PAGE_PROMPT = """Write the wiki page for ONE concept. Output ONLY markdown.

Structure exactly:
# <label>
## TL;DR {{#tldr}}
## Intuition {{#intuition}}
## Mechanics {{#mechanics}}
## The Math {{#the-math}}
## Go Deeper {{#go-deeper}}

Anchor rule (hard): every claim paragraph in Mechanics/The Math ends with a
semantic anchor like [§sec_3_2], [eq_1], or a research tag [S1]. TL;DR and
Intuition use the GLOBAL context only (no equations). Mechanics and The Math
use the LOCAL context. Go Deeper lists the note's resources with one-line whys.

Depth (hard): the reader has the paper. A tier that only restates it is a
wasted tier. Mechanics and The Math must do work the paper leaves implicit —
why a step is correct, what a quantity is doing, what breaks without it, why a
bound holds, what the cost is and where it comes from. Prefer the specific over
the summarising: name the objects, give the sizes, state the conditions.

Never write a tier whose content is that it has no content. "No equations were
supplied", "the local context does not include", "cannot be reproduced here"
and their paraphrases are forbidden — they tell the reader nothing they could
not see. If the LOCAL context has no display equation for this concept, The
Math still owes them real material drawn from what IS there: a worked example
with concrete values, a complexity or termination argument, a loop invariant,
a boundary case, or a derivation of the rule the prose states in words. Say
less, but say something true and load-bearing.

Write to be grasped quickly. Nothing here is a quota and none of it is checked
mechanically — you can see the content, so you pick the form. What the reader
needs is to find the point without mining for it, so strongly prefer:
- SHORT paragraphs over long ones. A big block is usually several claims
  stacked up; split it at the seams. Two or three tight paragraphs beat one
  dense one, and a paragraph past a handful of sentences is probably two.
- A bolded lead-in ending in a colon, then the explanation:
  **Why the bound is tight:** the estimate cannot ... [§sec_3]
  These read as subtitles and let the eye land on the right paragraph.
- BULLETS wherever the content enumerates at all — conditions, cases, steps,
  trade-offs. Prefer them to a sentence listing the same things with commas.
- A TABLE when two or more named things are compared on shared axes: two
  metrics, two graph classes, two algorithms and their costs.
- A ```mermaid graph when a relationship is structural and small (a graph, a
  dependency, a state change), never for decoration.
A tier with none of these shapes in it stays prose — formatting a paragraph
that is genuinely one argument only scatters it. Anchors still terminate every
claim, including list items, table rows, and each explanation inside the blocks
below.

CONTENT BLOCKS: where the LOCAL context supports it, emit one of these fenced
YAML blocks instead of describing the same thing in prose. They render as
interactive walkthroughs; prose about an algorithm does not.
- ```algorithm — pseudocode, one `intent` per line saying why that line is
  there. Use it whenever the concept HAS an algorithm or procedure.
- ```derivation — an equation reached in steps, each with its `why`.
- ```annotated-eq — one equation whose terms carry distinct roles (role: 1-5).
EARNED, NOT FORCED: emit a block only where the LOCAL context really contains
that shape. A concept with no algorithm gets no algorithm block; a concept that
is pure prose stays prose. Decorative blocks destroy the signal that a block
means "there is real structure here".

Exact syntax to follow:
{blocks}
Equations (hard): in The Math, reproduce each relevant equation from the LOCAL
CONTEXT [eq_N] entries VERBATIM as a display block wrapped in $$ ... $$ — keep it
as LaTeX, never convert to Unicode symbols — and put its [eq_N] anchor right after
the closing $$ on the same line. EVERY paragraph in Mechanics and The Math,
including the equation line, any lead-in sentence that introduces an equation,
and any honesty sentence, MUST end with an anchor ([§sec_x], [eq_N], or [S#]);
no exceptions. If a sentence introduces an equation, end that sentence with the
[eq_N] anchor before the $$ block.

GLOBAL CONTEXT:
{global_slice}

LOCAL CONTEXT:
{local_slice}
"""

PAGE_PROMPT = WRITING_SKILL + """

Use this exact structured-block syntax when a block is earned:
__BLOCK_SYNTAX__

GLOBAL CONTEXT:
__GLOBAL_CONTEXT__

LOCAL CONTEXT:
__LOCAL_CONTEXT__
"""


def _render_page_prompt(context: dict, rejected_for: list[str] | None = None) -> str:
    prompt = (PAGE_PROMPT
              .replace("__BLOCK_SYNTAX__", BLOCK_SYNTAX)
              .replace("__GLOBAL_CONTEXT__", context["global_slice"])
              .replace("__LOCAL_CONTEXT__", context["local_slice"]))
    if not rejected_for:
        return prompt
    # The retry used to re-send the identical prompt, which made it a re-roll
    # rather than a correction: six Transformer pages failed twice on the same
    # paragraph-length rule without ever being told. concepts.py already feeds
    # its validation errors back; this does the same.
    return prompt + (
        "\n\nYOUR PREVIOUS ATTEMPT WAS REJECTED. A deterministic check found:\n"
        + "\n".join(f"- {p}" for p in rejected_for)
        + "\nReturn the whole page again with exactly these problems fixed, "
          "changing nothing else. Splitting a long paragraph means finding the "
          "seam between its claims, not cutting it at a word count.")


def _spawn_claude(prompt: str) -> str:
    from .llm_spawn import claude_spawn
    # Roomier than the other stages on purpose. Once latex_pack started
    # recovering tables, a results page's LOCAL context grew by a 112-cell
    # grid; at max_turns=3/timeout=600 two Transformer pages died on the
    # ceiling rather than on their content ("Reached max turns", then a
    # timeout). The write stage gets one big prompt and owes a whole page,
    # so it is the stage that needs the headroom.
    return claude_spawn(prompt, max_turns=6, timeout=1800)


def _uncited_resources(page: str, note: dict | None) -> list[str]:
    """Note resources the page's Go Deeper tier never links.

    Fetching a lecture, verifying its video id and checking the note carries an
    explainer is all wasted if the page then does not link it -- and it did
    not: across the three aman.ai papers exactly 1 of 64 pages carried any
    external link in Go Deeper. Scoped to that tier because it is where a
    reader looks for what to read next; the same url buried in Mechanics is a
    different affordance.
    """
    urls = [r.get("url", "") for r in (note or {}).get("resources") or []
            if isinstance(r, dict) and r.get("url")]
    if not urls or "{#go-deeper}" not in page:
        return []
    deeper = page.split("{#go-deeper}", 1)[1]
    return [f"Go Deeper does not link the research resource {u}"
            for u in urls if u not in deeper]


def _page_problems(page: str, cid: str = "", pack: dict | None = None,
                   note: dict | None = None) -> list[str]:
    problems = ([f"missing tier {t}" for t in TIERS if t not in page]
                + pedagogy_problems(page, cid)
                + _uncited_resources(page, note))
    # Evidence discipline is the contract's central rule, and it used to be
    # checked only by p5_lint -- after the page was on disk, into a report that
    # blocks nothing. The DDIM run shipped 21 pages carrying 38 unanchored
    # claims and 7 no-content fillers, all of which had passed p4, because the
    # writer was never told. Checked here, a retry can actually fix them.
    #
    # Deterministic half only: lint_page's default link and mermaid checks make
    # network calls, and this runs up to MAX_WRITE_ATTEMPTS times per page.
    if pack is not None:
        from .p5_lint import lint_page
        problems += [p for p in lint_page(page, pack,
                                          check_links=lambda _url: True,
                                          check_mermaid=lambda _b: None)
                     if p not in problems]
    return problems


def _note_is_newer(cid: str, home, sentinel) -> bool:
    """Has this concept's research note been rewritten since its page was?

    Found by glob rather than by asking the wiki, which exposes no path. A
    concept with no note on disk is simply not stale, so a build with no
    research at all resumes exactly as it did before.
    """
    if home is None:
        return False
    try:
        written = sentinel.stat().st_mtime
        return any(f.stat().st_mtime > written
                   for f in Path(home).rglob(f"{cid}.yaml")
                   if "_inbox" not in f.parts)
    except OSError:
        return False


def write_pages(pack: dict, graph: dict, toc_rows: list, spawn=_spawn_claude,
                home=None, out_dir="pages", workdir=None, repo_dir=None) -> dict:
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parents[3]
                               / "Forked repos" / "graphify"))
        from graphify.exporters.explorer import reading_path
        order = {cid: i + 1 for i, cid in enumerate(reading_path(graph))}
    except Exception:
        order = {r["id"]: i + 1 for i, r in enumerate(toc_rows)}
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    done_dir = Path(workdir or ".") / "p4_done"
    done_dir.mkdir(parents=True, exist_ok=True)
    done, failed, skipped = [], [], []
    written: dict[str, str] = {}
    for row in toc_rows:
        cid = row["id"]
        # Resume skips work that is still CURRENT, not work that merely
        # happened. The sentinel alone meant "already written", so once
        # enrichment let P3 re-run on its own a note could be improved while
        # its page kept the old links -- on lottery-ticket that left 8 pages
        # older than their note and 21 resource urls uncited, none of them a
        # gate failure.
        if (done_dir / cid).exists() and not _note_is_newer(cid, home,
                                                            done_dir / cid):
            skipped.append(cid)
            continue
        note = wiki_get(cid, home=home)
        ctx = assemble_context(pack, graph, cid,
                               note["note"] if note["status"] == "ok" else None,
                               repo_dir=repo_dir)
        page, problems = "", ["spawn failed"]
        for attempt in range(MAX_WRITE_ATTEMPTS):
            try:
                page = spawn(_render_page_prompt(ctx, problems if attempt else None))
            except Exception as exc:
                problems = [f"spawn error: {exc}"]
                break
            problems = _page_problems(page, cid, pack,
                                      note["note"] if note and
                                      note["status"] == "ok" else None)
            if not problems:
                break
        if problems:
            inbox_add("failed-orchestration",
                      {"concept": cid, "phase": "p4", "problems": problems},
                      home=home)
            failed.append(cid)
            continue
        nn = order.get(cid, 99)
        filename = f"{nn:02d}_{cid}.md"
        (out / filename).write_text(page, encoding="utf-8")
        written[cid] = filename
        (done_dir / cid).write_text("done", encoding="utf-8")
        done.append(cid)
    return {"status": "ok", "done": done, "failed": failed, "skipped": skipped,
            "pages": written}


def annotate_graph(graph: dict, pages: dict) -> dict:
    """Copy ``graph`` with each written page recorded on its node.

    p4_write is the only stage that knows which file belongs to which concept,
    and downstream consumers ask the graph rather than the directory --
    viz.propose requires ``node["page"]`` outright, and without it reports zero
    candidates while blaming the pages. Returned as a copy rather than mutated
    in place: write_pages takes the graph as *input*, and silently rewriting a
    caller's dict is the kind of side effect that leaks across callers.
    """
    return {**graph, "nodes": [{**n, **({"page": pages[n["id"]]}
                                        if n.get("id") in pages else {})}
                               for n in graph.get("nodes", [])]}
