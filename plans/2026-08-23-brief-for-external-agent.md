# Brief: build 11 papers on another model backend

**Audience: an autonomous coding agent with shell access, working in this repo.**
You have no history with this project. Everything you need is below. Read the
whole brief before running anything — several of the instructions exist because
the failure they prevent has already happened here.

## What this project does

`paper-skill` turns an academic paper into a multi-page tutorial dashboard. Six
stages, each already implemented and tested:

| stage | does | LLM? |
|---|---|---|
| P1 `paper2pack` | paper → `pack.json` (sections, equations, tables, figures) | no |
| P2 `concepts` | pack → concept graph + `concept_toc.yaml` | yes |
| P3 `p3_research` | per-concept research notes with external resources | yes, **needs web search** |
| P4 `p4_write` | one tiered markdown page per concept | yes, **must have no tools** |
| P5 `p5_lint` | checks pages against the evidence | no |
| P6 `p6_explorer` | standalone HTML | no |

`run_pipeline.py` drives all six. **Your job is to run it for 11 papers.** You
are not being asked to redesign anything.

## State right now

Twelve papers were outstanding. One (`agentic-misalignment`) is finished on this
machine and is your **known-good baseline**: 21 of 22 pages, 0 lint findings,
and a dashboard bundle reading `7 image / 2 video / 8 link` embeds.

These 11 remain. All have `pack.json` already extracted, so P1 does not re-run
and nothing is re-downloaded:

`ai-control`, `refusal-direction`, `representation-engineering`,
`linear-representation`, `geometry-of-truth`, `sleeper-agents`,
`unfaithful-cot`, `autodan`, `universal-adversarial`, `pair-jailbreak`,
`harmbench`

`representation-engineering` (85 sections) and `ai-control` (50) are well above
the ~30 median and will run longer.

## Setup

```bash
# from the repo root, with research-mcp as a SIBLING directory
pip install -r requirements.txt
```

PowerShell (this is a Windows machine — note the `;` separator):

```powershell
$env:PYTHONPATH = "src;../research-mcp/src"
```

bash:

```bash
export PYTHONPATH="src:../research-mcp/src"
```

Confirm the suite is green before you change anything:

```bash
python -m pytest tests/ dashboard/tests/ -q
```

Expect ~749 passed, 1 skipped. **If it is not green, stop and report** — do not
build papers on a broken tree.

## Pointing the pipeline at your model

Every stage takes an injectable spawn, and `llm_spawn._backend_argv` reads two
environment variables. You do not need to edit any source file.

| variable | used by | leave unset to keep |
|---|---|---|
| `KE_LLM_CMD` | P2 concepts, P4 pages | the Claude CLI |
| `KE_LLM_CMD_TOOLS` | P3 research | falls back to `KE_LLM_CMD` |

The command is split with `shlex`, the prompt is written to **stdin**, and the
reply is read from **stdout**.

### Finding your model id

Do not guess it. List what your CLI actually offers and use the exact string:

```bash
opencode models          # or: opencode --help, to find the equivalent
```

Then, for example:

```powershell
$env:KE_LLM_CMD = "opencode run -m <exact-model-id>"
$env:KE_LLM_CMD_TOOLS = "opencode run -m <exact-model-id>"
```

If your CLI cannot read a prompt from stdin, do not fight it — write a wrapper,
put it on PATH, and point the variable at the wrapper:

```sh
#!/bin/sh
exec your-cli --prompt "$(cat)"
```

## Four requirements your backend must meet

These are not style preferences. Each one has already broken this pipeline.

1. **Prompt on stdin, reply on stdout.** Not as an argv argument — Windows caps
   a command line near 32,767 characters and P4 prompts exceed that. The failure
   is `WinError 206`, before the model is ever reached.
2. **Non-interactive.** No approval prompts, no TTY wait. A run that blocks on a
   prompt looks identical to a hung model.
3. **P4 must have NO tools.** Given a default toolset, the page writer explored
   the repo, read *finished sibling pages* — so a page gets built from other
   pages instead of the supplied evidence — and then called `Write` directly on
   the real artifact, bypassing the gate that inspects the returned string. If
   you cannot run your CLI tool-less, leave `KE_LLM_CMD` unset so P4 stays on
   Claude, and only set `KE_LLM_CMD_TOOLS`.
4. **P3 must have web search that actually fires.** Granting a tool is not the
   same as permitting it. With the Claude CLI, `--tools WebSearch` alone made
   the model reply *"I don't have permission to use WebSearch yet"* for 17 of 18
   concepts — logged as `not parseable JSON`, which sent the diagnosis in
   completely the wrong direction. `--allowedTools` was also required.

## Smoke test — do not skip this

Three separate bugs here were found only by reading one real reply. Two minutes
now saves hours.

```bash
python -c "
from paper_skill.llm_spawn import claude_spawn, _backend_argv
print('argv:', _backend_argv(6, ''))
print('reply:', repr(claude_spawn('Reply with exactly: OK')[:40]))"
```

Then a **valid** web-search probe. It must ask for something the model cannot
possibly know from memory — a probe it can answer from recall proves nothing.
A previous probe here asked for a well-known blog URL, "passed", and the tool
had never fired once:

```bash
python -c "
from paper_skill.llm_spawn import claude_spawn
print(claude_spawn('Search the web and reply with only the current top story headline on news.ycombinator.com', tools='WebSearch')[:200])"
```

A refusal, a permission request, or a plausible-but-stale headline all mean P3
is not really searching. **Stop and report** — the resource quality that
justifies this whole run depends on it.

## Running

One paper at a time, or several. Each is independent and the driver wraps every
paper in its own `try/except`, so one failure cannot cancel the rest:

```bash
python run_pipeline.py ai-control refusal-direction geometry-of-truth
```

**Run each paper twice.** This is measured, not superstition: the baseline paper
finished P4 at 15 done / 7 failed, and a plain re-run recovered 6 of the 7 in 17
minutes. The failures were stochastic — verbose paragraphs and a filler opening
in the maths tier — not a systematic defect. Sentinels (`p3_done/`, `p4_done/`)
mean the second pass retries only what failed and re-costs nothing else.

Budget **1.5–2.5 hours per paper** for the first pass. Eleven papers is an
overnight run.

## Verify each paper before trusting it

```bash
python - <<'EOF'
import json, pathlib, yaml
for a in sorted(pathlib.Path('artifacts').glob('*-live')):
    toc, pages, rep = a/'concept_toc.yaml', a/'pages', a/'p5_report.json'
    if not toc.is_file() or not pages.is_dir(): continue
    rows = (yaml.safe_load(toc.read_text(encoding='utf-8')) or {}).get('rows') or []
    n = len(list(pages.glob('*.md')))
    lint = len(json.loads(rep.read_text(encoding='utf-8'))) if rep.is_file() else '-'
    print(f'{a.name:34} concepts:{len(rows):3} pages:{n:3} missing:{len(rows)-n:3} lint:{lint}')
EOF
```

A healthy paper looks like the baseline: `missing` at 0–2, `lint` at 0.

Known failure modes, both of which have happened:

- **`P2 gate held after 3 attempts`** — the extracted graph looked like the
  paper's table of contents rather than a concept graph. The paper is skipped
  loudly. Report it; do not try to force it through.
- **Pages exist but are thin.** If a model cannot satisfy the pedagogy gates,
  what it did write is still recorded. Compare against the baseline medians:
  TL;DR 56 words, Intuition 100, Mechanics 256, The Math 190, Go Deeper 71.
  Pages far below those are a real problem even when nothing errored.

## Then build each dashboard bundle

```bash
cd dashboard
mkdir -p ../dashboards/<paper>/src ../dashboards/<paper>/public
python build_data.py --graph ../artifacts/<paper>-live/concept_graph.json \
  --pack ../artifacts/<paper>-live/pack.json \
  --pages-dir ../artifacts/<paper>-live/pages \
  --wiki-dir ../artifacts/<paper>-live/research_home \
  --assets-dir ../artifacts/<paper>-live/assets \
  --out ../dashboards/<paper>/src/data.gen.ts
```

It prints a line ending `embeds N image / N video / N link`. The baseline is
`7 image / 2 video / 8 link`. **An all-link tally means P3 found no visual or
lecture resources** — that is the signal that web search silently was not
working, and it is worth stopping over.

This step makes network calls; `--no-embed-probe` skips them but produces the
all-link tally, so do not use it while you are still validating.

## What to report back

For each paper: concepts, pages, missing, lint count, the embed tally, and the
wall-clock time. Plus:

1. The **exact** `KE_LLM_CMD` / `KE_LLM_CMD_TOOLS` you used and the model id.
2. The output of both smoke tests.
3. Any paper where the P2 gate held.
4. Anything that failed twice — that is the interesting signal, since a single
   failure is expected and a repeated one is not.

## Rules

- **Do not edit source to make a paper pass.** The gates exist because a bad
  graph or a filler page costs more downstream than a skipped paper. If a gate
  blocks something, report it.
- **Do not commit secrets.** `~/.config/opencode/config.json` on this machine
  contains a plaintext API key; do not copy it into the repo, a log, or a
  report.
- `dashboards/` is gitignored generated output. Artifacts under
  `artifacts/<paper>-live/` are the durable result — those are what to preserve.
- If you are unsure whether something is a bug or intended, report it rather
  than fixing it. Several things here look wrong and are load-bearing.
