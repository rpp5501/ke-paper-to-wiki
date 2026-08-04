# Proof: SID and SHD Relationship

## TL;DR {#tldr}
This concept establishes a formal link between two graph-comparison metrics: the Structural Hamming Distance (SHD) and the Structural Intervention Distance (SID). It proves that when SHD is zero, SID must also be zero, and more generally, that SID is bounded by a function of SHD — showing the two metrics agree in the trivial case and stay related as graphs diverge more.

## Intuition {#intuition}
SHD counts simple edge-level disagreements between two graphs, while SID counts disagreements in the causal effects those graphs imply. If two graphs are identical (SHD = 0), there's no reason their causal implications should differ, so SID should also be zero — this proof confirms that intuition holds. Beyond that trivial case, the proof shows a single edge change can only disrupt the parent sets of at most two nodes, giving a sense of how "local" edge errors translate into "global" interventional errors, and that this bound is tight rather than merely a loose upper limit.

## Mechanics {#mechanics}
The proof proceeds by cases on the value of the SHD between the two graphs. In the base case, an SHD of zero means every node has an identical parent set in both graphs, which makes every adjustment set valid and forces the SID to zero as well [§sec_10]. For the general bound, the argument relies on the observation that a single unit of SHD — one edge difference — can alter the parent set of at most two nodes, which limits how much the SID can grow per unit of SHD [§sec_10]. To show this bound is not merely an upper limit but actually achievable, the proof extends a construction from an earlier example to different nodes, and demonstrates sharpness by choosing the empty graph and a fully connected graph as the two graphs being compared [§sec_10].

## The Math {#the-math}
The local context describes this proof narratively and does not include a separate displayed equation; the referenced proposition and bound are stated and justified in prose rather than as a numbered [eq_N] formula [§sec_10].

## Go Deeper {#go-deeper}
No research note is attached to this concept, so there are no additional resources to list beyond the paper's own proof section, "Proof of Proposition (prop:sidshd)" [§sec_10].
