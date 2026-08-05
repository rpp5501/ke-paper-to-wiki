# Multiple Interventions (Future Work)

## TL;DR {#tldr}

SID as defined only scores predictions about single-node interventions; the paper flags extending it to *simultaneous* interventions on several nodes at once as unfinished work, because the adjustment-set argument that makes single-node SID computable does not carry over cleanly, and the number of interventions to check grows combinatorially with the number of nodes intervened on together.

## Intuition {#intuition}

SID works by asking, one node at a time, "would the estimated graph and the true graph agree on how the rest of the system responds if I intervened on this node?" That question has a clean answer because a single node's parent set is enough to shield it from confounding, so there is one obvious adjustment set to use. Once several nodes are intervened on together, the picture that made the single-node case tractable — one node, one parent set, one adjustment — no longer applies, and nothing in the current definition says what should replace it.

## Mechanics {#mechanics}

The result that lets single-node SID be computed from parent sets extends: a suitably modified version of the underlying lemma still holds when the intervention is on a set of nodes rather than one [§sec_2_4_7]. What breaks is the shortcut for using it. For a single intervened node, its parent set is guaranteed to be a valid adjustment set in the true graph; for several jointly intervened nodes, the union of their parent sets carries no such guarantee, even in the true graph itself [§sec_2_4_7].

Because that shortcut fails, scoring multi-node interventions would require a canonical rule for constructing *some* valid adjustment set for an arbitrary intervention set — a rule the paper does not supply [§sec_2_4_7]. Even granting such a rule, the number of intervention distributions to evaluate scales with how the possible interventions are enumerated:

- **Intervention sets per multiplicity**: for each number of nodes intervened on jointly, count the ways to choose which nodes those are [§sec_2_4_7].
- **Target nodes per intervention set**: for each such intervention set, any remaining node can be the one whose response distribution is compared [§sec_2_4_7].
- **Total intervention distributions**: summing this product over every multiplicity, from single-node interventions up to nearly all nodes at once [§sec_2_4_7].

Because that total grows quickly, the paper suggests addressing the two-node case first, as a middle ground between the already-solved single-node case and the full combinatorial problem [§sec_2_4_7]. A separate limitation survives any such extension: SID is a purely graphical criterion, so it cannot weigh *how strong* a causal effect is. If the estimated graph differs from the true one by a single edge, SID registers exactly one error regardless of whether that edge's effect is large or negligible [§sec_2_4_7].

## The Math {#the-math}

No display equations are given for this section, but the counting argument it describes in words can be made exact. Fix $p$ nodes and a multiplicity $k$ (the number of nodes intervened on jointly): the number of intervention sets is $\binom{p}{k}$, and each leaves $p-k$ candidate target nodes, so the per-multiplicity count and its sum over all multiplicities work out to a closed form [§sec_2_4_7].

```derivation
shape: Count how many intervention distributions multi-node SID would need to check.
steps:
  - latex: "\\binom{p}{k}(p-k)"
    why: "Choose which k of p nodes are jointly intervened on, then choose which remaining node is the target whose distribution is compared [§sec_2_4_7]"
  - latex: "\\binom{p}{k}(p-k) = p\\binom{p-1}{k}"
    why: "Algebraic rewrite: expanding the binomial coefficients shows the count is p times the number of size-k subsets of the other p-1 nodes [§sec_2_4_7]"
  - latex: "\\sum_{k=1}^{p-1} \\binom{p}{k}(p-k) = p\\sum_{k=1}^{p-1}\\binom{p-1}{k} = p\\left(2^{p-1}-1\\right)"
    why: "Summing over every multiplicity from 1 to p-1 and applying the binomial theorem shows the total number of intervention distributions is exponential in p [§sec_2_4_7]"
  - latex: "k=2:\\quad \\binom{p}{2}(p-2) = \\frac{p(p-1)(p-2)}{2}"
    why: "Restricting to the paper's suggested starting point of pairwise interventions still costs a cubic — not exponential — number of checks in p [§sec_2_4_7]"
```

Concrete values make the growth rate visible. At $p=3$ nodes, the total across all multiplicities is $3\left(2^{2}-1\right)=9$, matching a direct count: $k=1$ contributes $\binom{3}{1}\cdot 2=6$ and $k=2$ contributes $\binom{3}{2}\cdot 1=3$ [§sec_2_4_7]. At $p=10$, the same formula gives $10\left(2^{9}-1\right)=5110$, while restricting to pairs alone gives only $\binom{10}{2}\cdot 8=360$ [§sec_2_4_7]. This gap — exponential in $p$ for the full problem versus cubic for pairs — is the concrete reason the paper points to two-node interventions as the tractable first step rather than the general case [§sec_2_4_7].

## Go Deeper {#go-deeper}

- **Structural Intervention Distance (SID)** — the single-intervention criterion this section proposes extending; its parent-set adjustment argument is the piece that stops working once interventions are joint, so it's the prerequisite for understanding what's missing here.
