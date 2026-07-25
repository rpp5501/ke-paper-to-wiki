# You can now…

If this path did its job, each of these should feel checkable rather than aspirational:

- **Explain why average attack success is the wrong metric** — a mediocre overall ASR can hide subgroups that leak badly, and the reported number describes nobody in particular.
- **State the disparity definition precisely** — two disjoint subsets whose ASR gap exceeds a negligibility threshold \(\varepsilon\) — and say why the threshold and the choice of subsets both matter.
- **Trace the black-box pipeline end to end** — fabricate completions \(T(x)\), collect the confidence matrix \(\mathcal{C}\), fit per-class regression lines, and read off the angular difference \(\Delta\) as a correlation proxy no auxiliary data can give you.
- **Compute a vulnerability ranking** — sort groups by decreasing \(\Delta\) and know what Kendall's Tau against the true ASR ordering means (0.69–0.76 on Census19, vs. ~0 for an auxiliary-data baseline).
- **Run both targeted attacks on paper** — single-attribute (widest angular-difference spread, greedy from the top, budget \(\kappa\)) and nested (intersect above-average-risk segments of the top-d attributes).
- **Derive the controlled-sampling condition** — reduce Pearson's \(c\) to four cell counts and pin them down from \((n, m, c)\).
- **Argue the defense trade-off** — why BCorr (equalize the cause: per-group correlation) beats symptom-level fixes like DAMIR/MIR and fairness constraints, and what it costs (~33% of the training data).

If one of these still feels shaky, its chapter is one click away in the rail — or open the full map and follow the prerequisite edges down.
