# Proof: SID and SHD Relationship
## TL;DR {#tldr}
This proof pins down exactly how far SID and SHD can diverge: when two graphs are edge-identical (SHD = 0) their SID is also zero, but a single edge edit (SHD = 1) can still be blamed for a bounded — not unbounded — number of wrong intervention predictions, and the proof shows that bound is tight. The practical payoff is a warning: SHD is not a safe stand-in for SID, since a graph that is almost correct edge-by-edge can still misjudge many causal effects, and the two metrics can be pushed arbitrarily far apart by construction.

## Intuition {#intuition}
SHD is a local counter — it tallies single-edge edits separating two graphs and treats every edit as equally costly. SID is a global counter — it tallies how many source-target intervention questions the estimated graph gets wrong, and one bad edit can corrupt many such questions at once if it sits on the wrong node. The proof's job is to show that this corruption, while real, is not unlimited: one edge edit can only touch the parent sets of the two nodes it connects, so its damage to SID is contained rather than cascading through the whole graph. The empty-versus-fully-connected construction then shows how large that contained damage can still be.

## Mechanics {#mechanics}
The proof proceeds through four linked claims rather than one calculation, each covering a different regime of the SHD–SID relationship.

- **Zero-SHD base case:** if SHD(G, H) = 0, every node has an identical parent set in both graphs, so every adjustment set computed from H is also valid in G, forcing SID(G, H) = 0 as well [§sec_10].
- **SHD = 1 bound:** a single edge edit (add, remove, or reverse) can change the parent set of at most the two nodes the edge touches, so any resulting SID error must originate from just those two nodes [§sec_10].
- **Sharpness:** extending the same construction used earlier in the paper's worked example to additional nodes shows the SHD = 1 bound is achieved exactly, not merely satisfied with slack [§sec_10].
- **Extremal witness:** taking G as the empty graph and H as any fully connected graph on the same nodes realizes the general-case result, since these two structures maximize the gap the proposition allows [§sec_10].

The first claim is doing more work than it looks: "same parent set" is what makes an adjustment set valid at all, so equality of parent sets is both necessary and sufficient for SID to vanish, not just a sufficient condition the proof happens to use [§sec_10].

## The Math {#the-math}
No display equation is attached to this proof in the source material, but its logic is a clean counting argument that can be reconstructed step by step from the stated facts [§sec_10].

```derivation
shape: Bound the SID error caused by a single edge edit (SHD = 1).
steps:
  - latex: "\text{SHD}(G,H) = 0 \;\Longrightarrow\; \text{pa}_G(i) = \text{pa}_H(i) \;\; \forall i"
    why: "Zero edge differences means identical parent sets everywhere, so every adjustment set used to estimate an intervention effect is exactly the same set G would use [§sec_10]"
  - latex: "\text{pa}_G(i) = \text{pa}_H(i) \;\Longrightarrow\; \text{SID}(G,H) = 0"
    why: "Valid adjustment sets for every node mean every intervention distribution is computed correctly, so no (source, target) pair contributes to the SID count [§sec_10]"
  - latex: "\text{SHD}(G,H) = 1 \;\Longrightarrow\; |\{i : \text{pa}_G(i) \neq \text{pa}_H(i)\}| \le 2"
    why: "A single added, removed, or reversed edge only touches its two endpoints, so at most two nodes can have their parent set change at all [§sec_10]"
  - latex: "\text{SID}(G,H) \le 2 \cdot (p-1)"
    why: "Each of the at most two disturbed nodes can invalidate its own adjustment set for at most p-1 possible intervention targets, capping the total number of wrong (source, target) pairs [§sec_10]"
```

That last step is a deliberately loose upper bound built only from the text's counting logic, not a value asserted in the source; the sharpness claim is what tells you the true worst case sits at this order of magnitude rather than far below it [§sec_10]. The mechanism behind sharpness is a scaling argument: the same two-node disturbance used in the paper's earlier worked example can be replayed at any pair of nodes in a larger graph, so growing the graph while keeping SHD fixed at 1 keeps hitting the same bound instead of slack appearing [§sec_10]. The empty-graph/fully-connected-graph pair is the other extreme of the argument — it is not about SHD = 1 at all, but about showing that once SHD is allowed to grow without restriction, SID can be driven to its own maximum simultaneously, which is what "yields the result" for the unrestricted case [§sec_10].

## Go Deeper {#go-deeper}
- **Metric Properties of SID** — the parent concept this proof supports; it establishes SID as a well-defined pre-metric, and this proposition is the piece that relates it back to the more familiar SHD.
- **The worked example referenced mid-proof** (the paper's earlier Figure/Example that gets "extended to different nodes") — worth reading directly, since it supplies the concrete two-node construction this proof only describes abstractly.
