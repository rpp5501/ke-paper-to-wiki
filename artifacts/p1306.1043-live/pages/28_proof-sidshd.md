# Proof: SID and SHD Relationship
## TL;DR {#tldr}
This proof relates SID and SHD as part of SID's metric-like properties.

SHD zero forces SID zero. One edge disagreement moves SID by a bounded, sharp amount.

## Intuition {#intuition}
SHD counts local insertions, deletions, and reversals. SID counts global consequences: ordered pairs with wrong intervention distributions.

They live on different scales, so their relationship is not automatic.

A single edge changes at most two parent sets. Every other node's adjustment logic is untouched.

Zero edits therefore yield zero damage. One edit confines damage to two nodes, and sharpness shows this is worst-case rather than loose.

**Counterexample:** a one-edge reversal can keep SHD at one while changing a treatment row for every other target. Small structural edit distance therefore does not imply small intervention error [§sec_10].

## Mechanics {#mechanics}
**The zero case follows from definitions.** SHD$(G,H)=0$ gives identical edge and parent sets [§sec_10].

Every SID adjustment set is valid in both graphs, so no intervention pair differs and SID$(G,H)=0$ [§sec_10].

**The one-edit bound counts affected nodes.** An SHD unit changes parent sets only at an edge's two endpoints [§sec_10].

All other adjustment logic is unchanged. SID can gain errors only from two treatment rows, not the whole graph [§sec_10].

**Sharpness is constructive.** An earlier example shows one edge flip forcing maximal SID increase [§sec_10].

Repeating it on disjoint node pairs adds maximal damage without interference. The bound remains tight as SHD grows [§sec_10].

**The extremal pair is empty versus fully connected.** Every possible edge disagrees, maximizing SHD [§sec_10].

Empty-graph adjustment sets are valid nowhere in the fully connected structure, maximizing SID too. The general bound is attained with equality [§sec_10].

## The Math {#the-math}
**The one-edit bound is row counting.** With $p$ nodes, SID checks each $(i,j)$ with $i\neq j$, so every treatment node has $p-1$ targets [§sec_10].

An edge edit alters parent sets only at its endpoints. Only those treatment rows can change; all others agree between $G$ and $H$ [§sec_10].

At most $2(p-1)$ ordered pairs can flip per SHD unit because each affected node contributes at most $p-1$ targets [§sec_10].

Disjoint edits each spoil their full $p-1$ rows without overlap, so the additive bound is sharp [§sec_10].

Empty versus fully connected is the extreme count: up to $p(p-1)/2$ edges disagree and every node loses a valid adjustment set [§sec_10].

The empty graph's parent sets are all empty, none valid against dense $H$. The per-edit bound is a true worst case at any scale [§sec_10].

## Go Deeper {#go-deeper}
- **Metric Properties of SID** — the parent concept this proof supports; read it for why establishing SID(G,H)=0 ⇔ SHD(G,H)=0 and a bounded-growth relationship matters for treating SID as a well-behaved comparison measure between causal graphs, not just a heuristic score.
