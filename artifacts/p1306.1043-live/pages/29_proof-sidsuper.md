# Proof: SID for Superset Estimates
## TL;DR {#tldr}
This proof pins down exactly when SID(G,H) collapses to zero: precisely when the estimated DAG H never *drops* a true parent — every parent set in H contains the corresponding parent set in the true DAG G. The argument has two halves. First, it shows that adding extra parents to an adjustment set never breaks its validity, so an estimate that only over-includes edges reproduces every true intervention distribution exactly. Second, it shows the condition is tight: leave out even one true parent, and an adversarial distribution can be built where the estimate's answer provably diverges from the truth, forcing SID above zero.

## Intuition {#intuition}
Adjustment sets have a built-in slack: in a DAG, conditioning on more of a node's ancestors than strictly necessary doesn't corrupt an intervention calculation, so long as you don't accidentally condition on something downstream of the intervention. That's why a "superset" estimate — one that keeps every real edge and is free to bolt on spurious extra ones — can still get every interventional distribution exactly right.

Missing a real parent is a different kind of error entirely. It isn't slack, it's a hole: the adjustment formula silently drops the one variable needed to block a real confounding path, and there is no amount of extra edges elsewhere that can patch that hole. This is the structural reason SID treats false negatives (omitted edges) as categorically worse than false positives (added edges) — a theme that recurs throughout SID's metric properties.

## Mechanics {#mechanics}
The proof assumes $\mathrm{pa}_H(i) \supseteq \mathrm{pa}_G(i)$ for every node $i$ — H's parent sets are supersets of G's — and shows this forces SID$(G,H)=0$ by checking that H's parent sets remain valid adjustment sets once evaluated against the true graph G [§sec_9].

```algorithm
title: Forward direction — why a superset estimate has SID zero
lines:
  - code: "assume pa_H(i) ⊇ pa_G(i) for all nodes i"
    intent: "H never omits a true edge; it may only add extra ones [§sec_9]"
  - code: "check condition (a): no member of pa_H(i) lies on a directed i→j path in G"
    intent: "Directed paths in G use only G's edges, and every G-edge is present in H, so G's directed i→j paths are a subset of H's; a set that avoids all of H's directed paths automatically avoids the smaller set in G [§sec_9]"
  - code: "check condition (b): pa_H(i) blocks every non-directed i→j path in G"
    intent: "A non-directed path in G is built entirely from edges also present in H, so it is literally the same path in H with the same colliders and non-colliders; since pa_H(i) blocks it in H, it blocks it in G too — a path blocked in a DAG stays blocked in any sub-DAG that keeps that path's edges [§sec_9]"
  - code: "conclude pa_H(i) is a valid adjustment set for every (i,j) pair in G"
    intent: "Both conditions of the adjustment-set proposition transfer from H down to G, so the intervention distribution computed from H matches the true one for every pair, giving SID(G,H) = 0 [§sec_9]"
```

**Why the transfer only runs one way:** the argument leans on H being *larger* than G — extra edges in H can only create more directed paths and more candidate blocking structure to satisfy, never fewer. Going from "condition holds in the bigger graph" to "condition holds in the smaller graph" works because a path that survives in the smaller graph is a literal subset of the bigger graph's structure, not a new path with new colliders [§sec_9].

The converse direction shows the superset condition is necessary, not just sufficient: if H drops a true edge into some node $i$ that G has, the proof exhibits a concrete Markov distribution over G for which H's truncated adjustment set gives the wrong answer [§sec_9].

## The Math {#the-math}
**Setting up the counterexample:** take a node $i$ where G contains a parent that H's parent set for $i$ omits, and construct an observational distribution that is Markov with respect to $G$ by assigning the exogenous variables and the remaining structural assignments so that the omitted parent has a real causal effect on $i$'s distribution [§sec_9].

**Why the discrepancy is forced, not incidental:** because that parent is genuinely present in $G$, the true interventional distribution $p(x_j \mid \mathrm{do}(x_i))$ computed via $G$'s adjustment set depends on it; but the distribution computed via $H$'s adjustment set marginalizes it out entirely, since $\mathrm{pa}_H(i)$ never conditions on it. There is no cancellation available to make these two computations agree in general — the construction is free to choose the structural equations specifically so that the omitted variable's influence on $x_j$ is nonzero, which is exactly what a Markov-consistent distribution over $G$ permits [§sec_9].

**What this buys the proof:** finding one pair $(i,j)$ where the two computed distributions differ is exactly the definition of a nonzero SID contribution, so a single dropped true edge is already enough to push SID$(G,H)$ above zero — there is no partial credit for "almost" containing the true parent set [§sec_9].

## Go Deeper {#go-deeper}
- **Metric Properties of SID** — the parent proposition this proof serves; it's the broader argument (of which superset-estimate correctness is one case) establishing SID's behavior as a pre-metric, including why it is not symmetric under graph swap.
- **The adjustment-set validity proposition invoked in Step 1–2 above** — the two-condition characterization (no adjustment-set member on the causal path; blocking of all non-causal paths) that this proof reduces to, rather than re-deriving from scratch.
