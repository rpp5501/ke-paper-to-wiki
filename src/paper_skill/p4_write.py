"""P4 writers: one spawn per concept page, tier template enforced."""
from pathlib import Path
from research_mcp.inbox import inbox_add
from research_mcp.wiki import wiki_get
from .p4_context import assemble_context

TIERS = ("{#tldr}", "{#intuition}", "{#mechanics}", "{#the-math}", "{#go-deeper}")

PAGE_PROMPT = """Write the wiki page for ONE concept. Output ONLY markdown.

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

Format for scanning, not for prose volume: use a short bulleted list where the
content is genuinely a list, a small table where two or more things are being
compared on the same axes, a bolded lead-in clause where a paragraph turns on
one term. Do not force these — a paragraph that is genuinely a paragraph stays
one. Anchors still terminate every claim, including list items and table rows.
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


def _spawn_claude(prompt: str) -> str:
    from .llm_spawn import claude_spawn
    return claude_spawn(prompt, max_turns=3, timeout=600)


def _page_problems(page: str) -> list[str]:
    return [f"missing tier {t}" for t in TIERS if t not in page]


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
        if (done_dir / cid).exists():
            skipped.append(cid)
            continue
        note = wiki_get(cid, home=home)
        ctx = assemble_context(pack, graph, cid,
                               note["note"] if note["status"] == "ok" else None,
                               repo_dir=repo_dir)
        page, problems = "", ["spawn failed"]
        for attempt in range(2):
            try:
                page = spawn(PAGE_PROMPT.format(**ctx))
            except Exception as exc:
                problems = [f"spawn error: {exc}"]
                break
            problems = _page_problems(page)
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
