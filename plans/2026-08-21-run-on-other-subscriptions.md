# Running the remaining papers on another subscription

Goal: build the outstanding papers without spending this session's tokens. The
pipeline now takes its model backend from the environment, so another CLI can
do the work and the results merge back as plain files.

## What changed to make this possible

Every stage already accepted an injectable `spawn`, but `run_pipeline.py`
hardwired the Claude one. `llm_spawn._backend_argv` now reads two variables:

| variable | used by | default |
|---|---|---|
| `KE_LLM_CMD` | P2 concepts, P4 pages | `claude -p --max-turns N --tools ""` |
| `KE_LLM_CMD_TOOLS` | P3 research (needs web search) | falls back to `KE_LLM_CMD` |

Unset, behaviour is byte-identical to today — verified by test and by a live
call. Claude's own flags are deliberately **not** appended to an override; they
are claude-specific and another CLI would reject them as unknown arguments.

## The contract a replacement CLI must meet

Non-negotiable, because the stages assume all four:

1. **Prompt on stdin, reply on stdout.** Not as an argv argument — Windows caps
   a command line near 32,767 characters and P4 prompts exceed it.
2. **Non-interactive.** It must not prompt for approval or wait on a TTY.
3. **P4 must have no tools.** Left with a default toolset, the page writer
   explored the repo, read finished sibling pages, and called Write on the real
   artifact — bypassing `write_pages` and the pedagogy gate entirely. If the CLI
   cannot be run tool-less, do not use it for P4.
4. **P3 must have web search, and it must actually fire.** Granting a tool is not
   the same as permitting it: with Claude, `--tools` alone produced *"I don't
   have permission to use WebSearch yet"* for 17 of 18 concepts, logged as
   `not parseable JSON`. `--allowedTools` was required as well.

Output shape is forgiving: P2 and P3 want a JSON object and `parse_json_reply`
tolerates fences and narration around it; P3 also accepts YAML. P4 wants
markdown with the five tier headings.

## Setup on the other machine

```bash
git clone <this repo> && cd paper-skill
pip install -r requirements.txt      # or: pip install -e .
```

`research-mcp` must sit beside `paper-skill` as a sibling directory. Then set
`PYTHONPATH` — note the separator differs by platform:

```bash
export PYTHONPATH="src:../research-mcp/src"        # macOS / Linux
```

```bash
$env:PYTHONPATH = "src;../research-mcp/src"        # Windows PowerShell
```

Copy `artifacts/<paper>-live/` for each paper you intend to build. Each already
contains `pack.json` and `assets/`, so **P1 does not re-run and no paper is
re-downloaded** — the run starts at concept extraction.

## Per-CLI configuration

Verify the exact flags with `<cli> --help` before a long run; these are starting
points, not confirmed against your installed versions.

### Gemini CLI

```bash
export KE_LLM_CMD="gemini -p"
export KE_LLM_CMD_TOOLS="gemini --yolo -p"
```

`--yolo` auto-approves tool calls, which is what P3 needs and what P4 must not
have. Gemini's web search is a built-in tool, so nothing extra is required
beyond approval. **Check** that plain `gemini -p` does not still expose tools;
if it does, add whatever flag disables them, or use Gemini for P3 only.

### Codex CLI

```bash
export KE_LLM_CMD="codex exec"
export KE_LLM_CMD_TOOLS="codex exec --full-auto"
```

**Check** whether `codex exec` reads stdin. If it insists on a prompt argument,
it cannot be used unmodified — see the fallback below.

### A CLI that will not read stdin

Write a two-line wrapper that turns stdin into whatever the tool wants, put it
on PATH, and point `KE_LLM_CMD` at the wrapper. Nothing in the pipeline needs to
change:

```bash
#!/bin/sh
exec some-cli --prompt "$(cat)"
```

## Smoke test before committing to a long run

Do not skip this. Three separate bugs in this pipeline were found only by
reading one real reply.

```bash
python -c "
import os; os.environ.setdefault('KE_LLM_CMD','')
from paper_skill.llm_spawn import claude_spawn, _backend_argv
print('argv:', _backend_argv(6, ''))
print('reply:', repr(claude_spawn('Reply with exactly: OK')[:40]))"
```

Then a **valid** tool probe — one asking for something the model cannot know
from memory, because a probe it can answer from recall proves nothing:

```bash
python -c "
from paper_skill.llm_spawn import claude_spawn
print(claude_spawn('Search the web and reply with only the current top story headline on news.ycombinator.com', tools='WebSearch')[:200])"
```

If that returns a refusal, a permission request, or a plausible-but-stale
answer, P3 is not really searching and the whole point of the run is lost.

## Which papers, and how to split them

`agentic-misalignment` is building on this machine. Eleven remain, in the
tiered priority order already encoded in `run_pipeline.py`:

| tier | papers |
|---|---|
| 1 | `ai-control` |
| 2 | `refusal-direction`, `representation-engineering`, `linear-representation`, `geometry-of-truth` |
| 3 | `sleeper-agents`, `unfaithful-cot` |
| 4 | `autodan`, `universal-adversarial`, `pair-jailbreak`, `harmbench` |

Run one paper at a time, or several — each is independent and the driver already
wraps every paper in its own `try/except`, so one failure cannot cancel the rest:

```bash
python run_pipeline.py ai-control refusal-direction geometry-of-truth
```

**Split by subscription, not by stage.** Give each machine whole papers. Running
P3 on one model and P4 on another is possible (the artifacts are just files) but
means shipping `research_home/` between machines mid-build for no real gain.

Everything is resumable: sentinels (`p3_done/`, `p4_done/`) mean a re-run skips
completed work, so an interrupted run costs only the concept in flight.

## Expected cost and time

Measured on this machine, per paper: **P2** ~1 min, **P3** 10–36 min depending on
how many concepts sit at level ≤ 1 (6 concepts took 10 min, 18 took 36), **P4**
the largest share at roughly 20 pages × one spawn each with up to 6 turns.
Budget **1.5–2.5 hours per paper**; eleven papers is an overnight run, not an
afternoon.

`representation-engineering` (85 sections) and `ai-control` (50) are well above
the ~30 median and will take longer at P2 and P4.

## Verifying each paper before trusting it

```bash
python - <<'EOF'
import json, pathlib
for a in sorted(pathlib.Path('artifacts').glob('*-live')):
    p = a/'p5_report.json'
    pages = len(list((a/'pages').glob('*.md'))) if (a/'pages').is_dir() else 0
    lint = len(json.loads(p.read_text())) if p.is_file() else '-'
    print(f'{a.name:34} pages:{pages:3}  pages with lint findings:{lint}')
EOF
```

A healthy paper has roughly as many pages as concepts and few lint findings.
Two failure modes to watch for, both of which have happened:

- **P2 gate held after 3 attempts** — the graph came back looking like the
  paper's table of contents. The paper is skipped; nothing is silently wrong.
- **Pages exist but are thin.** If a weaker model cannot satisfy the pedagogy
  gates, `p4_done` still records what it wrote. Compare word counts against a
  known-good paper before accepting it (`Mechanics` median is 256 words).

## Merging results back

Copy the whole `artifacts/<paper>-live/` directory back. Then, here:

```bash
cd dashboard
python build_data.py --graph ../artifacts/<paper>-live/concept_graph.json \
  --pack ../artifacts/<paper>-live/pack.json \
  --pages-dir ../artifacts/<paper>-live/pages \
  --wiki-dir ../artifacts/<paper>-live/research_home \
  --assets-dir ../artifacts/<paper>-live/assets \
  --out ../dashboards/<paper>/src/data.gen.ts
```

That step makes network calls to classify resource urls; add `--no-embed-probe`
to skip them. `dashboards/` is gitignored generated output, so it must be
rebuilt after any pipeline change — see item 6 of the main plan.

## Risk worth stating plainly

The quality gates were tuned against Claude's output. A weaker or differently
tuned model may fail `graph_quality_findings` at P2 or the pedagogy gates at P4
more often — which is the system working, but it costs a run to discover.

**Build one paper on the new backend and inspect it before releasing the other
ten.** That is exactly the gate that caught three bugs on this machine, and it
costs one paper instead of eleven.
