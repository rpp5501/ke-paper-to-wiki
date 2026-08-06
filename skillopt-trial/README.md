# Paper-tutor SkillOpt benchmark

Target: `skills/write-paper-tutor/SKILL.md`. This benchmark optimizes the
page-writing contract only. React, AST extraction, schema validation, evidence
resolution, and mathematical truth gates remain deterministic code and are
never optimization targets.

The workflow follows SkillOpt's custom-benchmark model: define a benchmark
environment and editable artifact, choose an execution backend, establish a
baseline, train candidates, evaluate held-out tasks, and accept only a
validation-gated `best_skill.md`. This repository's gate is deliberately
offline: it checks recorded scores and evidence but never invokes SkillOpt, a
model, or an execution backend. Consult the [official SkillOpt
documentation](https://github.com/microsoft/SkillOpt/blob/main/README.md)
before using a backend because commands and requirements can change.

## Dataset split

- Train: SID and Transformer tasks. Candidates may learn from these outputs and scores.
- Selection: backdoor-paper tasks from `artifacts/p2205.06900-live`. Use them to select a candidate, never to train it.
- Final untouched test: privacy-paper tasks from `artifacts/p2504.04033-live`. Run once after selection; never revise the candidate from its results.

The exact manifest is `validation/tasks.json`; the weighted policy and
rejection rules are `validation/rubric.md`.

## Offline validation gate

`validation/validate_skillopt.py` uses only the Python standard library. It is
the executable and authoritative schema: exact-key checks in that file lock
the complete task manifest, rubric, score reports, hashed evidence references,
deterministic gates, and run ledger. There is no separate JSON Schema that can
drift away from runtime behavior.

Run these commands from `paper-skill/skillopt-trial` with Python 3:

```powershell
python validation/validate_skillopt.py policy
python validation/validate_skillopt.py report --report validation/fixtures/baseline-selection.json
python validation/validate_skillopt.py report --report validation/fixtures/candidate-final-test.json
python validation/validate_skillopt.py accept --baseline validation/fixtures/baseline-selection.json --candidate validation/fixtures/candidate-accepted-selection.json --run-record validation/fixtures/accepted-run-record.json
python -m unittest discover -s tests -v
```

`accept` exits 0 only for acceptance, 2 for a well-formed but rejected
candidate, and 1 for malformed input, broken policy, bad hashes, or an invalid
ledger. `policy`, `report`, and `accept` all enforce the same cryptographically
locked task manifest: IDs, prompts, concept IDs, artifact directories, target
skill, and paper/split mapping. Referenced artifact directories must exist and
match their paper.

A report's stage fixes its complete row set: `tuning` is SID and Transformer,
`selection` is backdoor, and `final-test` is privacy. Thus a final-test row
cannot be submitted as tuning input. Each report records its baseline or
candidate kind, hashed skill artifact, seven 0-100 rubric scores per row, hashed
raw output, automatic rejection flags, and all six deterministic gates. Every
gate has a `green` value and hashed local evidence; the combined source check
is consistently named `evidence_citation`.

Acceptance also requires a run record. Its hash-chained history is exactly
`tuning -> selection -> final-test -> human-review`, using timezone-aware,
strictly increasing timestamps. The tuning event binds one train-only candidate
report; selection binds the exact baseline and candidate report paths and byte
hashes; final-test binds one privacy-only candidate report. `accept` requires
the supplied selection paths and parsed content to match those bindings. The
ledger also binds the locked task-manifest hash, baseline and candidate skill
hashes, reviewed skill hash, reviewer identity, approval, and review timestamp.
The reviewed diff must equal the deterministic normalized unified diff between
the exact hashed baseline and candidate skill files; a merely well-hashed
placeholder is rejected. Paths are relative to this trial directory, may not
escape it, must exist, must be non-empty, and must match SHA-256. Fixture evidence is marked
`-text` in `.gitattributes` so checkout line endings do not change byte hashes.

The candidate must improve selection by at least 3 points, have no paper-level
regression over 2 points, carry no automatic rejection flag, keep all evidence
gates green, and have approved human review. Baseline rejection flags remain
auditable data but do not reject the candidate; baseline shape and deterministic
gates are still required. The current selection split has
only the backdoor paper, so its paper delta equals the overall selection delta:
the regression rule cannot independently reject a candidate that passes +3.
The checker still applies the rule generically to an explicitly re-locked
future multi-paper manifest; this benchmark does not invent another paper.

File references use raw-byte SHA-256. Ledger event hashes use SHA-256 over the
UTF-8 event object without `eventSha256`, serialized with sorted keys and
compact separators. The fixtures are illustrative offline records, not model
runs or evidence that SkillOpt executed.

## One bounded cycle

1. Validate the current project skill and run all deterministic tests.
2. Generate baseline pages and preserve raw outputs, scores, and hashes.
3. Configure a custom SkillOpt benchmark and execution backend whose only editable artifact is `skills/write-paper-tutor/SKILL.md`.
4. Train only on SID and Transformer. Bound edits to additions, deletions, and replacements inside that skill file.
5. Export and validate a `tuning` report; it may contain only the full train split.
6. Evaluate baseline and candidate on held-out backdoor rows and save separate `selection` reports. Do not run `accept` yet.
7. Run correctness, equation, evidence/citation, schema, component, and accessibility gates and record hashed evidence.
8. Freeze the selected candidate hash, then run privacy once as a separate `final-test` report. Never tune from it; no tuning or selection event may follow it.
9. Human-review the complete skill diff, recording reviewer identity, timestamp, reviewed skill hash, approval, and diff hash. Never auto-merge `best_skill.md`.
10. Complete the hash-chained run record and run `accept`. Selection scores decide improvement; final-test proves isolation and remains safety-gated, not tuning feedback.

## Infrastructure stop rule

If SkillOpt requires unwanted credentials, paid endpoints, or infrastructure,
stop the automated run. Apply the same bounded-edit flow manually: baseline,
train-only revisions, held-out selection, frozen-candidate final test, hashed
deterministic evidence, run ledger, and human diff review. The offline checker
is identical in either workflow and never replaces human judgment.

No baseline means no optimization. No green deterministic suite means no
acceptance.
