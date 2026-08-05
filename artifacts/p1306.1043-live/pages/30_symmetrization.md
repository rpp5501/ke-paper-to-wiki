# Symmetrization of SID

## TL;DR {#tldr}
SID was built to score an *estimated* graph against a *known true* graph, so it treats its two arguments differently. When you instead have two DAGs and neither one is privileged as the ground truth — comparing two learned structures, say — that asymmetry stops making sense, and you need a symmetric version of the same idea.

## Intuition {#intuition}
The original SID answers a directed question: "if I used H's parent sets to compute interventions, how often would I get the wrong answer relative to the true graph G?" That question only has a well-defined answer if one of the two graphs is trusted as correct. Symmetrization removes that privilege: it asks how much the two graphs disagree about interventional consequences, without designating either one as the reference. The natural way to do this is to run the original comparison in both directions and combine the results, so that either graph's mistakes count against the total.

## Mechanics {#mechanics}
The setting is two DAGs where neither can be regarded as an estimate of the other, which is exactly the case where directional SID is inapplicable [§sec_2_4_4]. The proposed fix is a symmetrized SID built from the original, directional quantity applied both ways rather than a distance invented from scratch [§sec_2_4_4]. The note is explicit that this is a **choice, not the only choice** — other constructions could equally well be called symmetric versions of SID [§sec_2_4_4].

A second construction is offered as an alternative: instead of combining two one-directional counts, count pairs $(i,j)$ whose intervention distributions coincide for *every* distribution that is Markov with respect to **both** graphs simultaneously [§sec_2_4_4]. This reframes symmetry as a shared-model condition rather than a sum of two asymmetric penalties, and it is symmetric by construction since "coincide" carries no direction [§sec_2_4_4].

| Construction | What it combines | Known weakness |
|---|---|---|
| Sum of directional SIDs | SID(G,H) and SID(H,G), each treating one graph as truth in turn | Not stated in the note, but inherits whatever biases directional SID has in each direction [§sec_2_4_4] |
| Shared-Markov coincidence | Pairs whose intervention distributions agree for all distributions Markov w.r.t. both G and H | Degenerates to zero whenever one argument is the empty graph [§sec_2_4_4] |

## The Math {#the-math}
No display equation for the symmetrized score survives in the local context, but the degeneracy the note flags is itself a precise claim worth deriving. The shared-Markov construction quantifies over *all* distributions consistent with both graphs' conditional-independence structure [§sec_2_4_4]. Take $H$ to be the empty graph: its Markov condition imposes full mutual independence among all variables, so the only distributions satisfying "Markov w.r.t. both $G$ and $H$" are ones where every variable is already independent of every other. For such distributions the intervention distribution $p(x_j \mid do(x_i))$ trivially equals the observational marginal $p(x_j)$ regardless of what $G$ says, so the coincidence condition holds vacuously for every pair $(i,j)$ [§sec_2_4_4]. The count of *disagreeing* pairs is therefore zero no matter how different $G$ actually is — the metric reports perfect agreement with an uninformative graph, which is the failure mode the note warns about [§sec_2_4_4]. This is the concrete reason the note treats the sum-of-directional-SIDs version as the more practically useful default, despite acknowledging it as one choice among several [§sec_2_4_4].

## Go Deeper {#go-deeper}
- **Structural Intervention Distance (SID)** — the directional quantity this construction symmetrizes; understanding what SID(G,H) counts is a prerequisite for seeing why summing it in both directions is the natural fix, and why the alternative construction can collapse against a trivial graph.
