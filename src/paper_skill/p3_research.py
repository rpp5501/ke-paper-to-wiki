"""P3: one leased researcher run per flagged concept. Deterministic shell;
LLM only inside spawn. Checkpoint per concept; resume free (round-4)."""
import argparse, json, sys
from pathlib import Path
import yaml
from research_mcp.inbox import inbox_add
from research_mcp.validate import lint_note
from research_mcp.wiki import wiki_get, wiki_put
from .briefs import build_brief
from .toc import load_approved_toc

RESEARCH_PROMPT = """Follow the research playbook loop for this brief, using
your own knowledge of well-known, real, reachable resources for this concept.
Output ONLY the finished note as YAML — no prose, no markdown code fences.

Use EXACTLY this shape and these key names:
concept: <the brief's concept slug>
status: complete | partial | insufficient-sources
synthesis: >
  2-6 sentences, at most 200 words. Tag each factual claim with [S1], [S2], ...
  where each tag matches a key in sources_consulted below.
resources:            # 1-4 items, each a real canonical URL for this concept
  - url: https://...
    title: ...
    type: visual | lecture | reference-impl | follow-up-paper | derivation
    why: one line on why it helps
unresolved:           # list of open questions (may be empty)
  - ...
sources_consulted:    # a MAP (not a list); keys are S1, S2, ...
  S1: citation or URL string
  S2: citation or URL string

BRIEF:
{brief_yaml}
"""


def _spawn_claude(prompt: str) -> str:
    from .llm_spawn import claude_spawn
    return claude_spawn(prompt, max_turns=15, timeout=900)


def _strip_fences(raw: str) -> str:
    """Peel a ```yaml ... ``` (or bare ```) code fence if the model wrapped the note."""
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        lines = lines[1:]                              # drop opening ```lang line
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]                         # drop closing ```
        text = "\n".join(lines)
    return text


def _parse_note(raw: str) -> dict | None:
    try:
        doc = yaml.safe_load(_strip_fences(raw))
        return doc if isinstance(doc, dict) else None
    except yaml.YAMLError:
        return None


def run_research(toc_path, graph: dict, spawn=_spawn_claude,
                 home=None, workdir=None) -> dict:
    toc = load_approved_toc(toc_path)
    if toc["status"] != "ok":
        return {"status": "not_approved", "hint": toc["hint"],
                "done": [], "failed": [], "skipped": []}
    done_dir = Path(workdir or ".") / "p3_done"
    done_dir.mkdir(parents=True, exist_ok=True)
    done, failed, skipped = [], [], []
    for row in toc["rows"]:
        if not row.get("research"):
            continue
        cid = row["id"]
        if (done_dir / cid).exists() or wiki_get(cid, home=home)["status"] == "ok":
            skipped.append(cid)
            continue
        brief = build_brief(row, graph)
        prompt = RESEARCH_PROMPT.format(
            brief_yaml=yaml.safe_dump(brief, allow_unicode=True, sort_keys=False))
        note, problems = None, ["spawn failed"]
        for attempt in range(2):                       # one retry max
            try:
                note = _parse_note(spawn(prompt))
            except Exception as exc:
                # A spawn EXCEPTION is a crash, not schema-invalid output —
                # fail immediately, do not retry.
                note, problems = None, [f"spawn error: {exc}"]
                break
            problems = lint_note(note) if note else ["not parseable YAML"]
            if not problems:
                break
        if problems:
            inbox_add("failed-orchestration",
                      {"concept": cid, "problems": problems}, home=home)
            failed.append(cid)
            continue
        wiki_put(cid, note, home=home)
        (done_dir / cid).write_text("done", encoding="utf-8")
        done.append(cid)
    return {"status": "ok", "done": done, "failed": failed, "skipped": skipped}


def main(argv=None):
    p = argparse.ArgumentParser(prog="p3_research")
    p.add_argument("toc")
    p.add_argument("--graph", required=True)
    a = p.parse_args(argv)
    graph = json.loads(Path(a.graph).read_text(encoding="utf-8"))
    print(json.dumps(run_research(a.toc, graph), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
