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
Honesty: if the local context lacks material for a tier, write one sentence
saying so rather than padding.

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
                home=None, out_dir="pages", workdir=None) -> dict:
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
    for row in toc_rows:
        cid = row["id"]
        if (done_dir / cid).exists():
            skipped.append(cid)
            continue
        note = wiki_get(cid, home=home)
        ctx = assemble_context(pack, graph, cid,
                               note["note"] if note["status"] == "ok" else None)
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
        (out / f"{nn:02d}_{cid}.md").write_text(page, encoding="utf-8")
        (done_dir / cid).write_text("done", encoding="utf-8")
        done.append(cid)
    return {"status": "ok", "done": done, "failed": failed, "skipped": skipped}
