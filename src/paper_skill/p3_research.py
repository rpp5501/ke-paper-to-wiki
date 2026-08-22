"""P3: one leased researcher run per flagged concept. Deterministic shell;
LLM only inside spawn. Checkpoint per concept; resume free (round-4)."""
import argparse, json, sys
from pathlib import Path
import yaml
from research_mcp.inbox import inbox_add
from research_mcp.validate import lint_note
from research_mcp.wiki import wiki_get, wiki_put
from .briefs import build_brief
from .candidates import candidate_block, find_candidates, paper_topic
from .resources import educational_gap, verify_resources
from .toc import load_approved_toc

# Level 0-1 is the concepts a learner meets first: about half of a paper's
# graph (9-13 of ~21 on the three aman.ai papers), which keeps the cost of
# enrichment to roughly ten calls per paper.
ENRICH_LEVEL = 1

# JSON, not YAML: a citation is normally written `"Quoted Title," Author, arXiv:...`
# and YAML reads the quoted title as a complete scalar, then fails on the author
# that follows. That killed the one research note in the chain-of-thought run,
# twice. The parser stays yaml.safe_load, which accepts JSON as a subset -- so a
# model that answers in YAML anyway still parses.
RESEARCH_PROMPT = """Follow the research playbook loop for this brief.
Output ONLY the finished note as a JSON object — no prose, no markdown fences.

You have WebSearch. USE IT for every resource you are about to cite, and cite
only what a search actually returned. Do not name a url from memory: recalled
urls look right and resolve to the wrong thing — two of fifteen arXiv ids
cited this way pointed at an unrelated paper, and both returned HTTP 200.
Search is also the only way to find what a learner needs, because the
explainers, lectures and animations below are not in any academic index.

Use EXACTLY this shape and these key names:
{{"concept": "<the brief's concept slug>",
  "status": "complete | partial | insufficient-sources",
  "synthesis": "2-6 sentences, at most 200 words. Tag each factual claim with
    [S1], [S2], ... where each tag matches a key in sources_consulted below.",
  "resources": [          // 1-4 items, each a real canonical URL
    {{"url": "https://...", "title": "...",
      "type": "visual | lecture | reference-impl | follow-up-paper | derivation",
      "why": "one line on why it helps",
      "anchor": "which part to actually consume — see below"}}],
  "unresolved": ["open questions, may be empty"],
  "sources_consulted": {{  // an OBJECT (not a list); keys are S1, S2, ...
    "S1": "citation or URL string",
    "S2": "citation or URL string"}}}}

These notes feed pages someone is trying to LEARN from, so include
at least one `visual` or `lecture`. What counts, concretely:

- a blog post or article that explains the idea (distill.pub, Lil'Log, Jay
  Alammar, aman.ai, Hugging Face blog, an author's own post)
- a diagram, animation or figure that shows the mechanism
- a recorded lecture or conference talk (YouTube, a course page)
- an interactive demo or notebook a reader can run
- a course or textbook section (d2l.ai, CS231n, CS224n and similar)

A list of papers and repositories is what a researcher cites, not what a
learner watches. Prefer the canonical explainer for this specific concept over
a general survey.

Well-known homes for this kind of material, as a starting point rather than a
list to pick from: distill.pub, Lil'Log, Jay Alammar, aman.ai, gwern.net,
colah.github.io, the Hugging Face blog and HF Learn, d2l.ai, Stanford CS231n
and CS224n, 3Blue1Brown, Computerphile, Two Minute Papers, Yannic Kilcher,
karpathy's repos and lectures, bbycroft.net/llm, poloclub's Transformer
Explainer, ml-visualized.com, seeing-theory.brown.edu, and an author's own
blog or talk. Prefer whatever is genuinely canonical for THIS concept.

For a `lecture`, give the direct video url — a YouTube `watch?v=` url or the
equivalent — NOT a course landing page or syllabus index. `efficientml.ai` and
`hanlab.mit.edu/courses/2023-fall-65940` are course indexes; the lectures
themselves are individual videos, and that is what a reader can actually
watch.

Set `anchor` on every resource: WHERE in it to look. A 40-minute lecture or a
long explainer is a chore to be handed whole. Name the timestamp range for a
video ("12:30-18:00, the derivation of the mask"), the section or heading for
an article ("the 'Why scaling?' section"), the file or function for a
repository ("model.py, the CausalSelfAttention class"), the section number for
a paper ("§3.2 and Table 2"). Be specific enough that the reader can go
straight there. If the whole thing is genuinely short and worth reading end to
end, say so plainly — do not invent a false precision.

Cite it only if it is real and you are sure of the url; a plausible guess is
worse than leaving it out, and a made-up link is checked and rejected. For a
YouTube video you must be sure of the video id itself — a real channel with an
invented id is still a dead resource. The same honesty applies to `anchor`: if
you do not know the timestamp or section, describe what to look for rather
than inventing a number.

BRIEF:
{brief_yaml}
"""


def _render_research_prompt(brief: dict, rejected_for: list[str] | None = None,
                            candidates: list[dict] | None = None) -> str:
    """Same correction the page writer gets: a retry that re-sends the identical
    prompt is a re-roll, not a fix. lint_note already says exactly which key is
    wrong -- withholding that from the one retry wastes it."""
    prompt = RESEARCH_PROMPT.format(
        brief_yaml=yaml.safe_dump(brief, allow_unicode=True, sort_keys=False))
    block = candidate_block(candidates or [])
    if block:
        prompt += (
            "\n\nVERIFIED CANDIDATES — these came back from a live search of "
            "arXiv, Semantic Scholar, OpenAlex and Crossref, so each title and "
            "url below is known to belong together. Prefer them. You may cite "
            "something else when it genuinely serves the reader better (a "
            "visual explainer or a lecture will not appear here), but only if "
            "it is real and you are sure of the url:\n" + block)
    if not rejected_for:
        return prompt
    return prompt + (
        "\n\nYOUR PREVIOUS NOTE WAS REJECTED. A deterministic check found:\n"
        + "\n".join(f"- {p}" for p in rejected_for)
        + "\nReturn the whole note again with exactly these problems fixed, "
          "changing nothing else.")


def _spawn_claude(prompt: str) -> str:
    from .llm_spawn import claude_spawn
    # The researcher is the one stage that must reach outside the prompt.
    # Its own instructions still say to work from recall, and recall is why
    # 2 of 15 cited arXiv ids resolved to a different paper than claimed --
    # and why the explainers a learner needs (distill.pub, a lecture) are
    # nearly absent: none of them are in the academic indexes candidates.py
    # federates. WebSearch only: it reads, it cannot touch the artifacts.
    return claude_spawn(prompt, max_turns=15, timeout=900, tools="WebSearch")


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
                 home=None, workdir=None, verify=verify_resources,
                 search=None, enrich_level=ENRICH_LEVEL) -> dict:
    toc = load_approved_toc(toc_path)
    if toc["status"] != "ok":
        return {"status": "not_approved", "hint": toc["hint"],
                "done": [], "failed": [], "skipped": []}
    done_dir = Path(workdir or ".") / "p3_done"
    done_dir.mkdir(parents=True, exist_ok=True)
    done, failed, skipped = [], [], []
    topic = paper_topic(graph)
    for row in toc["rows"]:
        # Two different questions. `research` is P2's answer to "is the paper's
        # own text insufficient here", which is nearly always no -- it flagged
        # 2 of 65 concepts across three papers, so P3 ran on 3% of the build.
        # The level test asks the learner's question instead: is this a concept
        # someone meets early and would want an explainer for. Bounded by depth
        # so enrichment cannot quietly research every concept in every paper.
        if not (row.get("research") or row.get("level", 99) <= enrich_level):
            continue
        cid = row["id"]
        if (done_dir / cid).exists() or wiki_get(cid, home=home)["status"] == "ok":
            skipped.append(cid)
            continue
        brief = build_brief(row, graph)
        # Once per concept, not once per attempt: the retry is a correction to
        # the same brief, and the candidates cannot have changed.
        found = find_candidates(brief, search=search, topic=topic)
        note, problems, gap = None, ["spawn failed"], []
        for attempt in range(2):                       # one retry max
            try:
                note = _parse_note(spawn(_render_research_prompt(
                    brief, (problems + gap) if attempt else None, found)))
            except Exception as exc:
                # A spawn EXCEPTION is a crash, not schema-invalid output —
                # fail immediately, do not retry.
                note, problems, gap = None, [f"spawn error: {exc}"], []
                break
            problems = lint_note(note) if note else ["not parseable JSON"]
            # Only once the shape is valid: resources on a note that failed the
            # schema may not even be a list, and one fault per round is what
            # the retry can actually act on.
            if note and not problems:
                problems = verify(note)
            gap = educational_gap(note) if note and not problems else []
            if not problems and not gap:
                break
        if problems:
            inbox_add("failed-orchestration",
                      {"concept": cid, "problems": problems}, home=home)
            failed.append(cid)
            continue
        # The gap costs the retry but never the note. P3 failing means the page
        # is written with no research context at all, so throwing away three
        # good papers for want of an explainer makes the page worse. Recorded
        # as a quality signal instead.
        if gap:
            inbox_add("resource-composition",
                      {"concept": cid, "problems": gap}, home=home)
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
