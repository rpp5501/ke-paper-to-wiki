# R14 validation rubric — explain skill (held-out gate)

Score each task 0–2 per dimension. Dimensions marked N/A for a task are
excluded and the task score is renormalized to 10. Grade with the same
keyless backend that runs the skill (claude_code_exec); the grader sees the
task prompt, the skill's output, and this rubric — never the skill text.

| Dim | 2 | 1 | 0 |
|---|---|---|---|
| **A. Output contract** | All five sections (Role, Relationships, Blast radius, Mechanics, Evidence and gaps) present, in order | Sections present but disordered or one missing | Contract ignored |
| **B. Evidence discipline** | Every factual claim cites a real path/anchor that exists in the fixture | Citations present but partly unverifiable or padded | Uncited claims presented as evidence |
| **C. Bridge integrity** | implements edges only asserted when confirmed; direction (code→concept) explicit | Confirmed bridge used but direction muddled | Any invented or reversed bridge (automatic 0) |
| **D. Gaps & staleness** | Missing pages/notes/edges surfaced plainly; not-found handled success-shaped | Gaps mentioned vaguely | Gaps papered over or fabricated content |
| **E. Scope discipline** | Narrow traversal (literal id searches, anchored tiers); no graph dump, no filler | Some over-reading but bounded | Whole-graph/pages dump or bloated output |

**Aggregate** = mean of task scores (each /10).

**Acceptance rule (validation gate):** a candidate SKILL.md edit is accepted
only if (a) held-out aggregate strictly improves over the current skill's
aggregate, AND (b) no individual task drops by more than 1 point. Rejected
edits go to the buffer, never merged.

**Baseline first:** before any sleep cycle, run all 10 tasks against the
current `skills/explain/SKILL.md` and record scores in
`skillopt-trial/results/baseline.json` — no baseline, no gate.
