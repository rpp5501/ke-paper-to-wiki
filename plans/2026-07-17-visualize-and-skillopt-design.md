# Visualize Feature + SkillOpt-Sleep — Design Decisions R13 & R14

**Status:** DESIGNED (2026-07-17), not implemented. Extends PLAN-v3; amends nothing in §5.1 (schema stays canonical and untouched).
**Canonical surface:** the learner-first dashboard (`paper-skill-slice9-bridge/dashboard`, per `plans/2026-07-14-learner-first-redesign.md`) — NOT the graphify explorer exporter. All viz work targets the dashboard.

---

## R13 — `visualize`: optional interactive explorables for important concepts

### Stance (token discipline, pinned)

Visualization is **opt-in, explicitly invoked, never automatic**. It does not run inside `paper2pack` or any default pipeline. Zero tokens are spent on visuals unless the owner runs the command/skill. A default build (no `--viz-dir`) must produce byte-identical output to today.

### What it is

Explorable-explanation-style interactive widgets (in the spirit of Setosa/Distill/MLU-Explain) for the handful of concepts in a paper where a static page genuinely under-serves understanding — attention, softmax temperature, positional encoding, gradient descent, and similar math-heavy mechanisms.

### Two generation tiers (owner decision: both)

1. **Template library (default, near-zero tokens).** Curated, parametric, self-contained HTML explorables shipped in `paper-skill/src/paper_skill/viz_templates/`. The skill's only LLM work is mapping concept → `template_id` + a small params JSON extracted from the node's page (labels, matrix dims, equation strings). Every template carries two standard affordances (exemplar research, `2026-07-17-viz-exemplar-research.md`): **reactive parameters** (scrub a value, everything downstream updates — Victor's reactive document) and **symbol↔visual linking** (hover an equation term ↔ highlight the visual element, both directions — CNN/Transformer Explainer pattern). v1 seed set:
   - `attention-heatmap` — seeded 4-token toy, live QKᵀ→softmax→weighted-sum heatmap; predict-then-reveal ("sketch the weights first"); √dₖ on/off toggle at growing dₖ (variance visibly explodes)
   - `softmax-temperature` — logit sliders + temperature dial; predict-then-reveal on the output distribution
   - `positional-encoding` — sin/cos wave stack with position/dimension scrubbers; linked to the encoding equation terms
   - `gradient-descent-2d` — click-to-drop start point on a loss surface, step-size dial; bet on where it converges before running
   - `vector-projection` — draggable vectors, live dot product / projection with reactive equation values
2. **Bespoke (explicit request only, full token cost).** LLM writes a one-off self-contained HTML explorable for a named concept that no template covers. Never selected automatically; the command requires the node id spelled out (`--bespoke <node-id>`). The generation prompt embeds the design rules and pattern catalog from `2026-07-17-viz-exemplar-research.md` — bespoke output follows the same contract as templates, not vibes.

**Design rules (pinned, from exemplar research):**
- **Seeded state, never blank.** Every viz opens mid-example on the concept's own values (Case's Sandbox-Mode deep-end warning — TensorFlow Playground overloads novices). Free-play unlocks after the guided interaction, never before.
- **Predict-then-reveal** wherever the concept has a right answer (Case Pattern #2, NYT You-Draw-It): the manifest `prompt` poses the bet; the viz reveals.
- **Scrub-only, no autoplay** — no play/pause chrome; direct manipulation over animation.
- **MathML, not KaTeX, inside iframes** — KaTeX css+fonts would blow the 150 KB cap; MathML is native and free.
- **Toy-sized honest data** (Setosa discipline): 3–5 tokens/points doing real arithmetic; no faked motion.

Uniform artifact either way: one self-contained HTML file per concept. Templates are instantiated by substituting a `{{PARAMS_JSON}}` placeholder — same embed path as bespoke, one code path downstream.

### Invocation

New sibling skill `skills/visualize/SKILL.md` (mirrors `skills/explain` in structure: workflow, token rules, common mistakes) plus a CLI *(as built — subcommands separate the token guard from generation)*:

```
python -m paper_skill.viz propose <concept_graph.json> --pages-dir <pages> [--k 4]
python -m paper_skill.viz build --params viz_params.json --pages-dir <pages> --out viz
```

`propose` prints candidates and stops (never generates). The LLM's only job is
authoring `viz_params.json` per the skill; `build` is deterministic
instantiation + gate. Bespoke stays a hand-invoked path documented in the skill.

- `--nodes`: explicit list, no selection logic.
- `--auto`: heuristic proposal, **hard cap K=4**: node's page exists on disk AND contains a The-Math tier (mandatory), ranked by degree desc then level asc. Prints the proposed list and template matches, then **stops for confirmation** before any generation. The cap and the confirm step are the token guards.
  *(Amended at build time 2026-07-17: the original "level ≤ 1" filter would exclude `scaled-dot-product-attention` (level 2) — the fixture's flagship math concept. The math-tier requirement already selects the right nodes; the level filter was dropped.)*

### Artifacts & contracts

- `viz/<node-id>.html` — self-contained, fully offline (no CDN, no `<link>`, no fetch; vendor anything needed inline, R12 discipline).
- `viz/manifest.json` — sidecar keyed by node id; **§5.1 is not touched**:

```json
{"attention": {"kind": "template", "template_id": "attention-heatmap",
  "src": "attention.html", "title": "Scaled dot-product attention, live",
  "caption": "Drag token vectors; watch QK^T -> softmax reweight the values.",
  "prompt": "Before you scrub: which token do you bet 'it' attends to most?",
  "page_sha256": "…", "generated": "2026-07-17"}}
```

`prompt` is required — the place-your-bets question shown before first interaction (see design rules above and the exemplar-research doc).

- `page_sha256` = hash of the source page at generation time → staleness detection.

### Gate: `paper-skill/scripts/gate_viz.py`

Every generated file (template or bespoke) must pass before it enters `viz/`:

1. No `http(s)://` refs, no `<link>`, no external `src` — grep-level offline check.
2. `</script>` injection guard on embedded params (reuse R12 explorer pattern).
3. Size ≤ 150 KB (it gets inlined into `data.gen.ts`).
4. Manifest entry present with title + caption + page hash.

Bespoke output additionally gets human review before commit — the gate checks safety/offline, not pedagogy.

### Steal-list additions (§7) — viz exemplars (licenses verified 2026-07-17)

| Repo | License | Take | How |
|---|---|---|---|
| vicapow/explained-visually | MIT | d3 explorable mechanics (eigenvectors, Markov chains, OLS, PCA) for templates | code |
| seeingtheory/Seeing-Theory | Apache-2.0 (+ attribution notice, crawl4ai precedent) | probability/stat explorables | code |
| poloclub/transformer-explainer | MIT | attention-matrix interactions, abstraction-level transitions | pattern + selected components |
| aws-samples/aws-mlu-explain | **CC-BY-SA 4.0 — ShareAlike, do NOT copy code** | comic-style scaffolding, scrollytelling structure | pattern-only |
| bbycroft/llm-viz | **no license file — all-rights-reserved** | 3D pipeline walkthrough concept | pattern-only |

Full exemplar research + pattern catalog: `plans/2026-07-17-viz-exemplar-research.md`.

### Dashboard surfacing (the "tab")

- `build_data.py --viz-dir viz/` (optional flag). When present, inlines each HTML as a string into `data.gen.ts` (one-way data flow preserved; never fetch at runtime). Absent → no change whatsoever.
- **Drawer tier "Visualize"**: rendered between Intuition and Mechanics, only for nodes with a manifest entry. Embedded as `<iframe srcdoc sandbox="allow-scripts">` (no same-origin — LLM-generated code stays sandboxed), lazy-mounted on tier expand so unopened visuals cost nothing at load.
- **Visuals gallery**: a TopBar entry (both modes) opening a panel that lists all manifest entries (title + caption); clicking one runs the existing `queueNavigation()` to the node and expands its Visualize tier. This is the "tab of important visuals" — it is an index over per-node visuals, not a separate rendering path.
- Staleness: if `page_sha256` no longer matches the page, `build_data.py` warns and the tier shows the existing staleness-banner treatment (codegraph pattern, round-9).
- UI-SPEC tokens (`2026-07-09-slice11-UI-SPEC.md`) apply to the tier/gallery chrome verbatim; iframe content is exempt but templates should default to the same palette.

### Exit test (acceptance, AIAYN fixture)

1. `viz build --auto` proposes ≤ 4 nodes and stops for confirmation.
2. `attention` renders the `attention-heatmap` template with seeded 4-token state, predict-then-reveal prompt, MathML term↔visual hover linking, and the √dₖ toggle; one bespoke explorable for a non-template concept passes `gate_viz.py`.
3. Dashboard built with `--viz-dir`: both visuals render offline (zero network requests), drawer tier + gallery navigation work, `npm test`/`pytest` green.
4. Dashboard built without `--viz-dir` is byte-identical to the pre-R13 build.

### Risks

| Risk | Mitigation |
|---|---|
| Token blowout on bespoke generation | Templates-first; `--auto` capped at 4 + confirm gate; bespoke requires explicit node id |
| Bespoke HTML quality/safety variance | `gate_viz.py` (offline/injection/size) + sandboxed iframe + human review before commit |
| Visuals drift as pages regenerate | `page_sha256` in manifest; build warns; staleness banner in tier |
| `data.gen.ts` bloat | 150 KB/file cap; lazy iframe mount; K=4 cap |
| Scope creep into a viewer rewrite | Viz is additive: one drawer tier + one gallery panel; canvas/store/modes untouched beyond a TopBar entry |

### Explicitly NOT in R13

No runtime LLM calls in the dashboard. No network embeds ever (vendor or don't ship). No viz path through the graphify explorer exporter. No auto-run inside `paper2pack`. No animation/video export. No new npm/pip dependencies.

---

## R14 — SkillOpt-Sleep trial for existing skills

**Repo:** microsoft/SkillOpt (MIT, verified 2026-07-17; v0.2.0, 2026-07-02). Text-space optimizer: scored rollouts → bounded add/delete/replace edits on a skill.md, accepted only on strict held-out validation improvement.

**Decision:** decline the full training loop (needs an optimizer-model backend + a benchmark env per skill — R11-1 friction, real infra). Adopt **SkillOpt-Sleep** — the nightly harvest→mine→replay→consolidate companion — via its **`claude_code_exec` backend**, which is subscription-side and keyless, therefore R11-1-compliant.

**Trial scope:** `skills/explain/SKILL.md` only. It is small, has a crisp output contract, and failures are observable.

**Validation set (build first, ~10 tasks):** held-out explain tasks over the AIAYN fixture + slice9 bridge graph — mixed concept/code/bridged nodes. Rubric (scored by the same keyless backend): output-contract sections present and ordered; evidence paths cited; no invented `implements` edges; staleness/gaps surfaced. An edit to the skill is accepted only on strict held-out improvement; rejected edits stay in the buffer.

**Hard rule:** the moment any step demands an API key or per-provider babysitting, the trial stops and we fall back to **pattern-only adoption** — the validation-gate discipline (bounded edits, held-out set, strict-improvement acceptance) applied manually to skill edits. The discipline is worth keeping even if the tool isn't.

**Exit test:** one full sleep cycle runs end-to-end with zero API keys and produces a `best_skill.md` diff + validation report; owner reviews the diff before anything merges into `skills/explain/SKILL.md`.

**Steal-list addition (§7):**

| Repo | License (verified 2026-07-17) | Take | How |
|---|---|---|---|
| microsoft/SkillOpt | MIT | skillopt-sleep loop (claude_code_exec backend) + validation-gated skill-edit discipline | pip tool, not forked; pattern-only fallback if keyless path breaks |

---

## Build order

1. ✅ **DONE 2026-07-17** — `gate_viz.py` + 2 templates + manifest contract (`src/paper_skill/viz.py`, `viz_templates/`, `scripts/gate_viz.py`, `scripts/build_viz_fixture.py`, `tests/test_viz.py` 19 green; fixture pack at `fixtures/viz/`, gate PASS, both files <11 KB).
2. ✅ **DONE 2026-07-17** — `build_data.py --viz-dir` (opt-in `viz` key, staleness vs manifest `page` hash) + `VizTier` drawer tier (lazy sandboxed iframe, stale banner) + `VizGallery` TopBar index + store `vizFocus`. Verified: dashboard pytest 35 green, vitest suite green incl. 5 new, `tsc --noEmit` clean (pre-existing `panelSizing.test.ts` missing-module error unrelated), default build byte-identical to committed `data.gen.ts` modulo CRLF.
3. ✅ **DONE 2026-07-17** — `viz propose`/`viz build` CLI in `paper_skill.viz` (propose = capped math-tier candidates + template suggestions, stops for confirmation; build = params-JSON → instantiate + gate, exit 1 on findings) + `skills/visualize/SKILL.md` (Deepwiki root). 26 pytest green; propose on the AIAYN fixture yields exactly `scaled-dot-product-attention → attention-heatmap`.
4. ✅ **Templates DONE 2026-07-17** — all five v1 templates shipped (`positional_encoding`, `gradient_descent_2d`, `vector_projection` added; each 7–10 KB, MathML + term↔visual linking + data-driven predict-then-reveal via `betOptions`/`betCorrect`/`betReveal` params; 32 pytest green, JS syntax-checked). **Bespoke path still unexercised** — deliberately left until a real concept needs it (it's the expensive one; the cheap path is proven).
5. R14: **trial kit DONE 2026-07-17** — `skillopt-trial/` at repo root (10 held-out tasks over the AIAYN fixture + bridge_mini incl. negative-control and not-found tasks; 5-dim rubric with acceptance rule; keyless runbook with the pattern-only fallback pinned). **Sleep cycle itself is owner-run** on the Windows host (needs Claude Code CLI + pip install skillopt); baseline scoring is the first step.
