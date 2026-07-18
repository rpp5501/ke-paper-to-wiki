# R14 — SkillOpt-Sleep trial on `skills/explain`

Decision: `plans/2026-07-17-visualize-and-skillopt-design.md` §R14.
Target: `skills/explain/SKILL.md`. Everything here runs **keyless**
(claude_code_exec backend, subscription-side) or not at all.

## Hard rule (pinned)

The moment any step demands an API key or per-provider babysitting: **stop**.
Fall back to pattern-only — apply the validation-gate discipline manually
(bounded add/delete/replace edits to SKILL.md, scored against
`validation/tasks.json` + `validation/rubric.md`, accepted only on strict
held-out improvement). The tasks and rubric in this kit work either way;
nothing depends on the SkillOpt tooling.

## One cycle (owner-run, on the Windows host)

1. **Install** (MIT, verified 2026-07-17):
   `pip install skillopt` (v0.2.0+ ships the `skillopt-sleep` CLI).
   Consult `docs/sleep/README.md` in microsoft/SkillOpt for the current
   config format — flags may have moved since this kit was written.
2. **Baseline** (required before any gate): run the 10 tasks in
   `validation/tasks.json` against the current skill via Claude Code
   (claude_code_exec), grade each with `validation/rubric.md`, save to
   `results/baseline.json` as `{task_id: {A..E, total}}` + aggregate.
3. **Sleep cycle**: point skillopt-sleep at this repo's Claude Code session
   history (harvest→mine→replay→consolidate), target skill
   `skills/explain/SKILL.md`, validation command = re-run step 2 on the
   candidate skill. Backend: `claude_code_exec` only — if the config insists
   on an OpenAI/Azure optimizer endpoint, invoke the hard rule above.
4. **Gate**: accept the candidate `best_skill.md` only if the rubric's
   acceptance rule passes (strict aggregate improvement, no task −1<).
   Keep rejected edits in `.skillopt/` (the buffer is part of the method).
5. **Review**: owner reads the diff before anything merges into
   `skills/explain/SKILL.md`. No auto-merge, ever.

## Exit test (from R14)

- [ ] One full sleep cycle end-to-end with zero API keys
- [ ] Produces a best_skill.md diff + validation report
- [ ] Baseline + candidate scores recorded in `results/`
- [ ] Owner reviewed the diff before merge

## Layout

```
skillopt-trial/
  README.md                  this runbook
  validation/tasks.json      10 held-out explain tasks (never for training)
  validation/rubric.md       5-dim scoring + acceptance rule
  results/                   baseline.json, candidate-*.json (created at run time)
```
