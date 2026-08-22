# Improvement plan — 2026-08-21

Every number here is measured against the 226 page files in `artifacts/*-live/pages`
and the six bundles in `dashboards/`. Where an earlier claim was wrong, the
correction is stated rather than quietly dropped, because two of them changed
what is worth building.

## Corrections that changed the priorities

**The on-ramp is not being drowned.** I reported "~170 words of TL;DR + Intuition
against a 1,150-word Go Deeper" more than once. That came from splitting
`data.gen.ts` on tier headings, which sweeps the JSON resource arrays into the
last tier. Measured on the page files:

| tier | median | mean | min | max |
|---|---|---|---|---|
| TL;DR | 56 | 60 | 26 | 149 |
| Intuition | 100 | 107 | 49 | 267 |
| Mechanics | 256 | 279 | 55 | 713 |
| The Math | 190 | 197 | 18 | 931 |
| Go Deeper | **71** | 70 | 7 | 184 |

On-ramp share is a median 23%, p10 15%, min 12% — one page out of 226 below 12%.
The distribution is tight, so there is no thin tail to gate on. Whether 23% is
the right share is a **design decision, not a defect**, and resource enrichment
never made it worse. A pedagogy gate here would either fire on nothing or force
a corpus-wide rewrite on my taste. Not built. See item 4.

**chain-of-thought's missing math is correct.** Its pack has 0 equations and
`equation_fidelity: "exact"`. The source genuinely has no `equation`/`align`
environments — its only `$…$` are symbol escapes (`$\langle$`, `$\sim$`). Not an
extraction bug. The "rescue chain-of-thought" item is void.

**Figure placement is ~50%, not 26%.** ddim places 6 of 13 pack figures, resnet
6 of 7, lottery-ticket 22 of 45. My earlier number compared image *files* to
figure *blocks*; one figure holds several images.

**Anchors are clean.** 13 `§` characters, zero U+FFFD, in the file I suspected.
The corruption I thought I saw was my console's cp1252 mangling the output.

## Done

**P3 retrieves instead of recalling** (`361664b`). `--tools ""` was added to
`claude_spawn` to stop the page writer calling `Write` on the real artifact, but
`claude_spawn` is shared — so a P4-specific guard also removed P3's ability to
reach anything, while P3's prompt still said to work from its own knowledge.
`tools` is now a parameter defaulting to `""`; P3 asks for `WebSearch` only.

This is the root cause of every resource defect measured: 2 of 15 cited arXiv
ids resolved to a different paper (both HTTP 200), and the explainers a learner
needs are nearly absent because distill.pub, a blog post and a lecture appear in
**no academic index** — so `candidates.py`'s federated arXiv/S2/OpenAlex/Crossref
search can never surface one, however well it works.

**`visual` resources render as preview cards** (`7221dd9`, `75f60eb`). Honest
yield 6 of 27; the naive version claimed 14 and 8 were generic social cards or
broken.

## Sequenced plan

The order matters: item 1 gates item 2, and item 2 is the expensive one.

### 1. Verify P3 retrieval on one paper — before spending anything else

The fix is committed and **has never been run**. Building 13 papers on an
unproven researcher risks 13 papers' worth of tokens producing the same recalled
URLs, or worse, a stage that now hangs on WebSearch turns.

Run P3 alone against one already-built paper into a scratch home and diff the
notes against the committed ones.

- **Verify:** resources per note stay 1–4; `type` distribution gains `lecture`
  and non-arXiv `visual`; every URL HEADs alive; `verify_resources` reports zero
  title mismatches. Compare `embed_kind(..., want_preview=True)` yield against
  today's 6/27.
- **Watch for:** turn-count blowup. P3 runs at `max_turns=15`; WebSearch turns
  count against that, and a researcher that spends 15 turns searching returns
  nothing.
- **Cost:** one paper, ~10–13 enriched concepts (`ENRICH_LEVEL = 1`).

### 2. Build the 13 unbuilt papers

Not 12 — `artifacts/` holds 13 with a pack and no pages: agentic-misalignment,
ai-control, autodan, geometry-of-truth, harmbench, linear-representation,
neural-cleanse, pair-jailbreak, refusal-direction, representation-engineering,
sleeper-agents, unfaithful-cot, universal-adversarial.

**Pre-flight, before spending a token:**

- `neural-cleanse` extracted **1 section from a PDF**. Every other paper used the
  LaTeX path with 13–85 sections. Building it now produces a garbage dashboard.
  Re-extract or drop it.
- `representation-engineering` has 85 sections and `ai-control` 50, against a
  median of ~30. Expect longer P2/P4 and a larger concept graph.
- `aiayn` has pages but **no `pack.json`** — it cannot be rebuilt or re-linted
  as things stand.

Run through `run_pipeline.py`, which is resumable via sentinels and already
carries a per-paper `try/except`. `concept_toc.yaml` is a human checkpoint — 13
of them is the real bottleneck, not compute.

- **Verify per paper:** P5 report clean; `build_data.py` prints a non-zero embed
  tally; pages ≈ concepts.
- **Cost:** roughly 12 × a full P1–P6. This is the item to schedule against a
  fresh limit window, not to start at the end of a session.

### 3. Decide `pack["references"]`

Verified: written in `latex_pack.py`, `paper2pack.py` and `references.py`, and
**read nowhere** — no consumer in `briefs.py`, `p4_write.py`, `build_data.py`, or
any component. Its extraction has been fixed twice for nothing (natbib
`\bibitem[...]{key}`, then the `.bib` fallback).

Three options, in ascending cost:

- **Delete it.** Smallest diff; loses a correct extractor.
- **Ship it as a panel.** The bundle already carries the data; a references list
  in the drawer is a small React change and no new writer tokens.
- **Give it to the writer.** Most valuable and most expensive: a new anchor
  namespace (`[R7]`) the linter must learn, plus prompt tokens per page.

Recommended: the panel. It uses what is already extracted without adding a
namespace to a linter that has already been the source of one 30-failure
incident.

### 4. On-ramp — a decision, not a gate

The measured share is 23%, tightly distributed. If you want a wider on-ramp, the
lever is the **writing contract** in `skills/write-paper-tutor/SKILL.md`, not a
deterministic gate, and it needs a target chosen deliberately — 30%? 35%? — then
a rebuild to see whether the writer complies. Do this *after* item 2, so the
change lands on all 19 papers at once instead of splitting the corpus into two
styles.

### 5. Raise the `visual` preview yield

21 of 27 `visual` URLs have no `og:image`, including jalammar.github.io and
transformer-circuits.pub — two of the best explainers in the set, both full of
inline diagrams. The next step is a first-in-content-image fallback: same GET
already being made, take the first sufficiently large `<img>` when the meta tag
is absent.

Cheap, but it needs the same real-URL probe discipline as the og:image work —
the unit tests passed on a version that shipped the arXiv logo and a broken
`<img>`. Do it after item 2 so it is measured against 19 papers, not 6.

### 6. Make the bundle rebuild a script

`build_data.py` was invoked by an ad-hoc six-paper shell loop with five path
flags each. `dashboards/` is gitignored generated output, so every pipeline
change silently leaves stale bundles until someone re-runs that loop from
memory. A small `rebuild_dashboards.py` over `artifacts/*-live` removes a
standing footgun.

## Not doing

- **Stanford STORM as a dependency.** Its headline output — outline plus
  Wikipedia-style article — duplicates P2's human-approved `concept_toc.yaml` and
  P4's tiered pages, and it drags dspy + litellm + a search backend into a
  pipeline whose entire LLM surface is one `subprocess.run(["claude", ...])`. The
  one idea worth taking was retrieval grounding, which is item 1 and is done. Its
  second idea — multi-perspective question asking, mapped onto the tiers — is
  worth revisiting only after item 4 fixes a target.
- **A pedagogy gate on tier proportions.** See the correction above.
