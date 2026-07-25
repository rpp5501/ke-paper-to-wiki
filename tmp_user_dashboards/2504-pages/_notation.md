# Notation guide

Every recurring symbol in this paper, one line each.

| Symbol | Meaning |
|---|---|
| \(\mathcal{M}\) | the target model under attack (black-box: returns a label and a confidence) |
| \(\mathbb{D}\) | the dataset the model was trained on |
| \(\mathbb{D}_i\) | a subgroup of \(\mathbb{D}\), carved out by a non-sensitive attribute value |
| \(\mathcal{N}(\mathbb{D})\), \(n(x)\) | the non-sensitive portion of the data / of one record — the adversary's view |
| \(s(x)\), \(\mathcal{S}\) | a record's true sensitive value, and the set of possible sensitive values |
| \(\mathcal{A}\) | the attack algorithm (CSMIA, LOMIA, ...) |
| \(ASR\) | attack success rate — fraction of records whose secret the attack recovers |
| \(\mathrm{ASRD}\) | attack success rate *difference*: widest ASR gap among groups; the disparity metric |
| \(\varepsilon\) | negligibility threshold below which a gap does not count as disparity |
| \(T(x)\) | a record's hypothetical completions — one per candidate secret |
| \(\mathcal{C}\) | the confidence matrix: model confidences for every completion of every record |
| \(t\) | prediction-correctness vector — the adversary's only quality signal |
| \(\Delta\), \(\Delta_\angle\) | angular difference: mean pairwise angle between per-class regression lines; the black-box proxy for correlation |
| \(c\) | Pearson correlation between the sensitive attribute and the output |
| \(m\) | ratio of negative-sensitive to positive-sensitive records in controlled sampling |
| \(n_+^-\) (etc.) | cell counts: subscript = sensitive value, superscript = output |
| \(\kappa\) | attack budget: fraction of the dataset the targeted attack aims at, in (0, 0.5] |
| \(q\), \(\mathbb{D}_q\) | query budget and the sampled subset queried under it |
| \(R = (r_1, \dots, r_k)\) | vulnerability ranking of groups, most vulnerable first |
| \(\mathbb{D}_{target}\) | the subset a targeted attack commits its budget to |
| \(c_m\), \(D_i'\) | BCorr: the lowest group correlation, and group \(i\) resampled to match it |
