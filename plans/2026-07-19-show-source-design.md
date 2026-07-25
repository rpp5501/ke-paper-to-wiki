# Show-Source Passage — Design + Implementation Plan (R15.11)

**Status:** ✅ BUILT 2026-07-19 (subagent-executed: Sonnet 5 python slice,
Opus 5 TS slice; orchestrator gate). All 5 steps verified: dashboard pytest
47/47 (3 new), vitest 52/52 in touched files (source vectors shared PY↔TS),
tsc clean, `data.gen.ts` regenerated — only diff is the `sections` key
(golden-file test enforces this).
**Pattern source:** Denser Chat's highlight-the-sourcing-passage idea,
adapted to our offline/one-way-data-flow architecture.
**Working dir:** `paper-skill-slice9-bridge/` (branch `slice9-bridge`).

## Goal

Selecting a node in the dashboard lets the learner open the *actual paper
passage* the node was extracted from — offline, zero new deps. Deepens the
pinned moat (pedagogy + provenance): every claim traceable to the paper span.

## Design

**Data flow (build-time, one-way, unchanged discipline):**
- Graph nodes already carry `source_ref` ("sec:3.2" style). Pack already
  carries `sections: [{id: "sec_3_2", title, level, text}]`. Today
  `build_data.py` uses sections only for `eqIndex` and drops the text.
- New: when `--pack` is passed, `build_bundle` emits
  `bundle["sections"] = {section_key(s["id"]): {"title": ..., "text": ...}}`
  reusing the existing `section_key()` normalizer (joins `sec_3_2` ↔
  `sec:3.2`). Follows the `mtimes`/`repo_dir` precedent: keyed on an existing
  flag, no new flag; builds without `--pack` are untouched.
- `--update` mode does NOT need changes (sections ride with full builds;
  patching sections alone is out of scope — YAGNI).

**Dashboard:**
- `src/lib/source.ts`: `sectionFor(node, sections)` pure function —
  normalizes `node.source_ref` via the same key logic (port `section_key`
  to TS in this file), returns `{ref, title, text} | undefined`.
- `SourcePanel` in `Drawer.tsx` render tree, after the tiers section and
  before the code viewer: a `<details className="source-tier">` with summary
  `Source: §{ref} {title}` and the passage text in a `<blockquote>`.
  Renders nothing when the bundle has no `sections` key or the node's ref
  doesn't resolve (missing evidence is silent here — the Evidence-and-gaps
  reporting lives in the explain skill, not the reading UI).
- Component follows the established Presentation split
  (`SourcePanelPresentation({entry})`) for static-markup tests.

**Explicitly not in scope:** PDF-page rendering or in-PDF highlighting (we
have no PDF in the bundle; the pack's extracted text IS the source of
record), per-sentence spans (pack granularity is section-level today),
patching sections via `--update`.

## Implementation steps (each → verify)

1. `build_data.py`: extract the `section_key` helper to module level (it is
   currently nested inside `_eq_index` — move, don't duplicate; `_eq_index`
   calls the moved function). Add `sections` emission under `if pack:`.
   → verify: new pytest `test_build_data_sections.py` — emitted with pack
   (fixture: key "3.2" → title "SDPA", text "t"), absent without pack;
   `_eq_index` behavior unchanged (existing tests green).
2. `dashboard/src/lib/source.ts`: `sectionKey()` TS port + `sectionFor()`.
   → verify: vitest — resolves "sec:3.2" and "sec_3_2" to the same entry;
   returns undefined for missing ref/empty sections.
3. `Drawer.tsx`: read `KE_DATA.sections ?? {}`, render `SourcePanel` after
   the tiers/viz section. Presentation component in
   `src/components/SourcePanel.tsx`.
   → verify: vitest static-markup — panel shows §ref + title + text; renders
   nothing without sections; existing Drawer tests green.
4. `styles.css`: `.source-tier` styles (UI-SPEC tokens; blockquote muted,
   border-left accent).
   → verify: styles.test.ts green (it lints token usage).
5. Full gate: mirrored pytest suite, vitest suite, `tsc --noEmit`
   (ignore pre-existing panelSizing error), and a `--pack` build whose only
   diff vs before is the `sections` key.

## Exit test

Build with the standard fixture command (includes `--pack`); select
`scaled-dot-product-attention`; a "Source: §3.2 SDPA" details element opens
to the pack's section text, fully offline. A build without `--pack` is
byte-identical to pre-R15.11.

## Risks

| Risk | Mitigation |
|---|---|
| Fixture pack text is a stub ("t") — demo looks thin | Structurally correct now; real value lands with the first real paper2pack run. Note in demo. |
| `section_key` drift between PY and TS ports | Same test vectors asserted in both suites (step 1 + step 2 share cases: `sec_3_2`, `sec:3.2`, `§3.2`, `Sec 3.2.1`). |
| Drawer.tsx keeps growing | SourcePanel is its own file; Drawer only mounts it. |
