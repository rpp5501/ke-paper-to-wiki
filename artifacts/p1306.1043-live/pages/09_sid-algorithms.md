# SID Algorithms
## TL;DR {#tldr}
SID is made computable by two paired algorithms: one that walks every node pair in the DAG and checks whether the estimated graph predicts the right causal effect, and a helper routine that figures out, for each node, which other nodes are reachable from it along paths that a valid adjustment set would not block. Together they turn the abstract definition of Structural Intervention Distance into something that can actually be run on an adjacency matrix. This machinery sits directly on top of the SID implementation and depends on the theory of causal effects in linear Gaussian SEMs to know what "correct causal effect" even means.

## Intuition {#intuition}
Rather than comparing two causal graphs edge by edge, SID asks a more practical question for every ordered pair of nodes: if you intervened on the first node, would the second graph correctly tell you the causal effect on the second node? Answering that for every pair naively would mean re-deriving adjustment sets and path-blocking conditions from scratch each time, which is slow and repetitive. The algorithms exist to avoid that repetition — they precompute reachability information once per node and reuse it, and they use a compact "path matrix" representation so that checking whether an effect is predicted as zero, correct, or wrong becomes a fast lookup instead of a fresh graph search.

## Mechanics {#mechanics}
The main algorithm takes two adjacency matrices of the same size — one for the true DAG, one for the estimated graph — and proceeds node by node: for a given source node it computes the parents in the estimated graph, builds a path matrix that encodes which nodes are reachable without traversing an edge that leaves the parent set with a "tail," and uses a second path matrix to find nodes reachable from the source via paths that are not blocked by that parent set. [§sec_12]

For every target node it then compares what the path matrix predicts against what the true graph implies: if the true parents of the target (excluding the source) are not all in the estimated adjustment set, the estimated graph is checked against whether it too predicts a zero effect, and a mismatch between the two predictions (one says zero, the other doesn't, or they disagree on sign/existence) counts as one structural intervention mistake. [§sec_12]

The per-target mismatches for a given source are accumulated by summing over the path matrix and over the two categories of incorrect predictions (mistakes arising from missing adjustment versus mistakes arising from divergent path predictions), and the algorithm's overall output is the sum of these mistakes over all source nodes — this total is exactly the Structural Intervention Distance. [§sec_12]

The second algorithm, "rondp" (finding all reachable nodes on non-directed paths), is the reachability subroutine that the main algorithm depends on: given a node, its parents, its children, and the two path matrices, it builds a reachability matrix where each entry is tagged by whether the node was reached via an outgoing or an incoming edge, and it propagates reachability outward — a parent of an already-reachable node is itself marked reachable if it isn't already in the "blocked" set, and analogous propagation rules are applied on the children side. [§sec_12]

Because a plain reachability sweep can still miss some nodes — for instance when a directed, unblocked path exists from the source to a node whose own parents should therefore also count as reachable — the routine runs a follow-up pass that uses the auxiliary path matrix to detect this case, adds the missing parent nodes to the reachable set, and then recomputes the path matrix a second time so the final output reflects the corrected reachability set. [§sec_12]

## The Math {#the-math}
The local context describes both algorithms only in pseudocode and prose (parent/children computations, path-matrix construction, reachability propagation, and mistake counting); it does not include a numbered display equation ([eq_N]) for this concept, so no formula is reproduced here. [§sec_12]

## Go Deeper {#go-deeper}
- **Implementation of SID** — the parent note where these two algorithms are actually assembled into working code; useful for seeing how the pseudocode here maps to a real function signature.
- **Causal Effects in Linear Gaussian SEMs** — the prerequisite theory that defines what a "correct" versus "incorrect" causal-effect prediction means, which is the quantity these algorithms are counting mismatches of.
