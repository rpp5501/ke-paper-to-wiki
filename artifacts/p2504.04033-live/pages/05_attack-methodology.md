# Attack Methodology
## TL;DR {#tldr}
Attack Methodology is the umbrella for the two attack classes this paper introduces on top of the Attack Threat Model: a disparity inference attack that ranks groups by how vulnerable they are to attribute inference, and a targeted attribute inference attack that uses that ranking to pick high-risk groups and attack them directly. Both attacks are built on a shared primitive, angular difference, which is why Computing Angular Difference sits at the center of this concept rather than being a detail of just one attack. The methodology is positioned between Uncovering High-Risk Groups, which it builds on, and Experiments, which validates it, while the paper's mitigation strategies and related work are framed as contrasting responses to the vulnerability this methodology exposes.

## Intuition {#intuition}
The core idea is that not all groups in a dataset leak their sensitive attribute equally — some groups' records make the model's confidence scores shift much more dramatically when the sensitive attribute is hypothetically changed, which makes them easier to attack. Rather than attacking every record with the same blind strategy, the adversary first measures this "shiftiness" per group and then concentrates effort where it pays off most. This two-step logic — measure vulnerability, then exploit the most vulnerable — is what separates disparity inference (just ranking and reporting which groups are at risk) from targeted attribute inference (actually using that ranking to break privacy for the highest-risk subset).

## Mechanics {#mechanics}
Both attack classes reduce to the same underlying operation: computing angular difference over groups of records, so the methodology begins by detailing that shared technique before branching into the two attacks [§sec_5]. The disparity inference attack applies angular difference across candidate groups and uses the resulting values purely to rank groups by attack vulnerability, without necessarily launching a further inference step [§sec_5]. The targeted attribute inference attack reuses that same ranking machinery but adds a second phase: it strategically selects target subsets identified as high-vulnerability and then launches attribute inference attacks specifically against those subsets, rather than attacking uniformly [§sec_5]. This makes the angular-difference computation a prerequisite subroutine that both attacks call, which is why the methodology treats it as a first-class part of the section rather than an implementation detail buried inside either attack [§sec_5].

## The Math {#the-math}
The methodology first builds a confidence matrix by querying the target model on a dataset whose non-sensitive portion is held fixed while the sensitive attribute is varied, producing a matrix of model confidences together with a boolean vector marking which predictions were correct [§sec_5].

$$
\text{Confidence Matrix Generation}
$$ [§sec_5]

Given that confidence matrix and the correctness vector, the second procedure computes the angular difference for a group by fitting regression lines through the confidence-derived points for the records in that group and averaging the angle between all pairs of those lines, yielding one angular-difference value per group [§sec_5].

$$
\text{Angular Difference Computation}
$$ [§sec_5]

The local context describes these two procedures at the level of named algorithms with their input/output roles (target model, non-sensitive data, confidence matrix, correctness vector, per-group angular difference) but does not carry explicit numbered equation formulas beyond these algorithm definitions, so no further [eq_N] content can be reproduced here without fabrication [§sec_5].

## Go Deeper {#go-deeper}
No research note is attached to this concept, so there are no external resources to cite here. Within the wiki, the natural next stops are Computing Angular Difference (the shared subroutine both attacks depend on), Disparity Inference Attack and Targeted Attribute Inference Attack (the two concrete instantiations of this methodology), and Experiments (where the methodology is empirically validated).
