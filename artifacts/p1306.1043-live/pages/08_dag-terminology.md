# DAG Terminology
## TL;DR {#tldr}
Structural Intervention Distance compares a true DAG against an estimated graph, and the estimate is very often not a single DAG but an equivalence class of them — so before SID can be defined, the paper has to fix a shared vocabulary for graphs, orientations, and the "same independence structure" relation that groups DAGs into classes. This page collects that vocabulary: subgraphs, parents and skeletons, directed paths and ancestry, PDAGs and chain graphs, and the Markov-equivalence machinery that turns a set of indistinguishable DAGs into one CPDAG. Every later SID definition — what counts as an adjustment set, what it means to compare a DAG to a CPDAG — leans on these terms without re-deriving them.

## Intuition {#intuition}
A graph carries two kinds of information that are worth separating: *which pairs of variables are connected at all* (the skeleton), and *which direction, if any, each connection points* (the orientation). SID needs both, because the skeleton alone doesn't tell you who can be used to adjust for confounding, and the orientation alone doesn't tell you two graphs are "close" as unlabeled structures.

Directed paths encode a causal ordering — an ancestor can influence a descendant, never the reverse — and this is what makes a DAG acyclic in the first place: no descendant can loop back to be its own ancestor. Blocking a path is the graph-theoretic stand-in for "no information flows here": a **fork or chain** (a middle node with the arrows pointing away, or straight through) shuts the path down once you condition on the middle node, while a **collider** (a middle node with both arrows pointing in) does the opposite — it's closed by default and only opens once you condition on it or something downstream of it.

Markov equivalence is the idea that two differently-drawn DAGs can imply the exact same conditional-independence structure, so no amount of observational data could ever tell them apart. A CPDAG is the compressed representation of that whole equivalence class: an edge stays directed only if every DAG in the class agrees on its direction, and becomes undirected the moment the class disagrees. This is why SID has to define comparisons against CPDAGs, not just DAGs — it's the natural output of causal discovery from observational data.

## Mechanics {#mechanics}
**Subgraphs and skeletons separate structure from orientation.** $H$ is a subgraph of $G$ when its nodes and edges are subsets of $G$'s, and a proper subgraph when it is missing at least one edge; the skeleton discards direction entirely, treating $i \to j$, $i \leftarrow j$, and $i - j$ as the same undirected connection between $i$ and $j$ for the purpose of counting edges [§sec_7].

**Adjacency and parenthood are the two vocabularies edges are read in.** Two nodes are adjacent if any edge connects them in either direction; $j$ is a parent of $k$ (and $k$ a child of $j$) specifically when the edge is directed $j \to k$, so "adjacent" is the skeleton-level notion and "parent/child" is the oriented one layered on top of it [§sec_7].

**Directed paths generate the ancestor/descendant partition that acyclicity depends on.** A path is a sequence of distinct, pairwise-adjacent nodes; if every edge on it points the same way, it is a directed path, and its endpoint is a descendant of its start (equivalently the start is an ancestor of the endpoint) [§sec_7]. Every node not reachable this way is, by definition, a non-descendant — this partition is what "no directed cycle" is a statement about: a DAG forbids any pair where each node is a descendant of the other [§sec_7].

**A semi-directed cycle is what a PDAG must avoid, and a collider is what turns a path from open to closed.** A cycle back to the starting node counts as semi-directed once at least one of its edges is truly directed rather than undirected; a node in the middle of a path is a collider precisely when both of its neighboring edges point into it ($j \to k \leftarrow l$) [§sec_7]. PDAGs forbid directed cycles, chain graphs additionally forbid semi-directed cycles between any pair, and within a chain graph the nodes reachable from one another purely by undirected edges form an equivalence class called a chain component [§sec_7]. A DAG is the special case of a PDAG where every single edge is directed [§sec_7].

## The Math {#the-math}
The paper states the blocking rule for a path given a conditioning set $S$ as a case split on the middle node $k$, and the two cases are structurally opposite — worth walking through side by side rather than just quoting.

```derivation
shape: When does a middle node k block a path through it, given a conditioning set S (with the path's endpoints not in S)?
steps:
  - latex: "\\text{Case 1: } k \\text{ is not a collider on the path } (j \\to k \\to l \\text{ or } j \\leftarrow k \\to l)"
    why: "k passes information through by default — it is a valve that is open unless you shut it [§sec_7]"
  - latex: "k \\in S \\;\\Rightarrow\\; \\text{path is blocked}"
    why: "Conditioning on a non-collider fixes it, cutting the chain or fork it sits on [§sec_7]"
  - latex: "\\text{Case 2: } k \\text{ is a collider on the path } (j \\to k \\leftarrow l)"
    why: "A collider is a valve that is closed by default — the two arrowheads meeting at k block flow unless something forces it open [§sec_7]"
  - latex: "k \\notin S \\text{ and no descendant of } k \\text{ is in } S \\;\\Rightarrow\\; \\text{path is blocked}"
    why: "This is the reverse condition of Case 1: conditioning on a collider (or its descendant) opens the path instead of closing it — the two cases cannot be merged into one rule [§sec_7]"
```

A path between disjoint sets $X$ and $Y$ is $d$-separated by $S$ only when *every* path between them is blocked by this rule, and the joint distribution is Markov with respect to the graph when $d$-separation implies conditional independence, faithful when the converse holds too [§sec_7]. Two DAGs are Markov equivalent exactly when they entail the same set of $d$-separations — a purely graphical criterion that never has to touch the distribution itself [§sec_7].

That equivalence relation is what makes the CPDAG well-defined: it is the chain graph obtained by comparing every DAG in an equivalence class edge by edge.

```algorithm
title: Building the completed PDAG (CPDAG) of a Markov equivalence class
lines:
  - code: "for each pair (i, j) adjacent in some member DAG:"
    intent: "The CPDAG's skeleton is the union of skeletons across the class — equivalent DAGs share the same skeleton, so this is really just one DAG's skeleton [§sec_7]"
  - code: "    if all members orient the edge i -> j the same way:"
    intent: "Unanimous orientation means every DAG consistent with the observed independencies agrees here, so it is safe to assert the direction [§sec_7]"
  - code: "        mark edge as directed i -> j"
    intent: "This is the causally-identifiable part of the class — no additional data could ever resolve it further [§sec_7]"
  - code: "    else if members disagree on the edge's direction:"
    intent: "Disagreement means the direction is genuinely unidentifiable from the independence structure alone [§sec_7]"
  - code: "        mark edge as undirected i - j"
    intent: "Undirected marks exactly the ambiguity that SID later has to handle when its input is a CPDAG rather than a DAG [§sec_7]"
```

The cost of this construction is linear in the number of skeleton edges once the equivalence class's member DAGs (or their $d$-separation statements) are known — each edge only needs a single unanimous/split check, not a re-scan of the whole class per edge [§sec_7].

## Go Deeper {#go-deeper}
- **Structural Intervention Distance (SID)** — the direct successor concept: SID is defined on top of exactly this vocabulary, since its inputs are a true DAG and an estimated DAG *or* CPDAG, and its adjustment-set machinery is built from parent sets and $d$-separation as defined here.
- No research note is attached to this concept; the terminology itself is the resource — treat this page as the reference to return to whenever a later SID definition invokes "skeleton," "collider," "Markov equivalent," or "CPDAG" without re-explaining it.
