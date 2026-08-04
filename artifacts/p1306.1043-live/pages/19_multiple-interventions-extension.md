# Multiple Interventions (Future Work)

## TL;DR {#tldr}
Structural Intervention Distance (SID) is defined for single-node interventions; extending it to simultaneous interventions on several nodes at once is flagged as unresolved future work, building directly on the core SID framework.

## Intuition {#intuition}
SID works by asking, for every node, whether the true parent set is a valid adjustment set in the estimated graph — a question that only makes sense one node at a time. Once you intervene on several nodes together, the clean notion of "parents of this node" no longer settles what needs to be adjusted for, so the same yes/no logic that makes SID simple to compute and interpret for single interventions doesn't carry over cleanly to the multi-node case.

## Mechanics {#mechanics}
A modified version of the underlying lemma used to score single interventions still holds when intervening on multiple nodes, but the union of the individual parent sets is no longer guaranteed to be a valid adjustment set — even when evaluated against the true causal graph itself [§sec_2_4_7]. This forces a shift from checking a naturally given adjustment set (the parents) to needing a canonical, explicitly constructed choice of valid adjustment set for each intervention target [§sec_2_4_7]. Beyond the graphical criterion itself, actually computing this at scale requires handling the combinatorial blow-up: for a given multiplicity of simultaneous interventions there is a large number of possible intervention sets and possible target nodes, so a practical starting point is to first restrict attention to the two-node case before considering the fully general problem [§sec_2_4_7].

## The Math {#the-math}
The local context does not include a worked-out formula or equation for the multi-intervention case — the section explicitly describes this as an open extension rather than a completed derivation, so no display equation can be reproduced here [§sec_2_4_7]. It does note a structural limitation of any purely graphical criterion: because SID cannot take the strength of causal effects into account, two estimated graphs differing by one edge would both incur the same distance-of-one penalty relative to the true graph, even though the practical cost of missing a strong edge versus a weak edge can differ substantially [§sec_2_4_7].

## Go Deeper {#go-deeper}
No research note is attached to this concept, so no external resources are available to list — the material above is drawn solely from the paper's own discussion of open problems, including a reviewer comment suggesting this speculative section be either deleted or folded into a more concrete "Extensions" section alongside the symmetrized SID and PDAG variants.
