# DAG Terminology
## TL;DR {#tldr}
Before comparing two causal graphs, you need a shared vocabulary for what a graph is: which nodes are related, which paths carry dependence, and which graphs encode the same independence structure. This page collects that vocabulary — parents, ancestors, colliders, blocked paths, Markov equivalence — as the ground floor beneath Structural Intervention Distance (SID), which asks whether two DAGs imply the same causal effects even when they aren't identical as graphs.

## Intuition {#intuition}
Two ideas carry the weight. First, a DAG only partially reveals causal structure: several different DAGs can produce the exact same observable independence pattern, so they get bundled into a Markov equivalence class and drawn as one composite object — a CPDAG — whose directed edges are the orientations every member of the class agrees on, and whose undirected edges mark genuine ambiguity. Second, whether a path between two variables carries dependence depends on what you already know: conditioning on a common cause or an intermediate variable closes a path that was open, but conditioning on a common effect (a collider) can open a path that was closed. These two ideas — equivalence classes and conditioning-dependent blocking — are exactly what SID has to work around when a graph doesn't fully pin down which variables to adjust for.

## Mechanics {#mechanics}
A graph $H$ is a **subgraph** of $G$ if its nodes and edges are subsets of $G$'s; it is a *proper* subgraph if that inclusion is strict. This gives SID a way to compare an estimated graph against the true one edge-by-edge rather than only as opaque wholes [§sec_7].

**Parents, children, and adjacency** are read directly off directed edges: $X$ is a parent of $Y$ (and $Y$ a child of $X$) if there's a directed edge $X \to Y$, and two nodes are adjacent if any edge connects them in either direction. The **skeleton** discards direction entirely, counting an edge once regardless of orientation — this is the object two Markov-equivalent DAGs must share exactly [§sec_7].

A **path** is a sequence of distinct adjacent nodes; a **directed path** additionally requires every edge to point forward, which is what makes $Y$ a **descendant** of $X$ and, symmetrically, $X$ an **ancestor** of $Y$. Ancestry, not mere adjacency, is what later determines valid adjustment sets for intervention distributions [§sec_7].

A **collider** on a path is a node where both neighboring edges point into it ($\to m \leftarrow$); a **semi-directed cycle** is a path that returns to its start with at least one directed edge along the way. Colliders matter because they reverse the usual rule for when conditioning closes a path [§sec_7].

| Graph class | Defining constraint | Anchor |
|---|---|---|
| PDAG | no directed cycle (no pair with directed paths both ways) | [§sec_7] |
| Chain graph | no *semi-directed* cycle (stronger: even mixed cycles are excluded) | [§sec_7] |
| DAG | a PDAG in which every edge is directed | [§sec_7] |

The three classes nest: every DAG is a chain graph, every chain graph is a PDAG, and each added constraint is what buys the stronger structural guarantee — full acyclicity for DAGs, freedom from mixed cycles for chain graphs [§sec_7]. In a chain graph, nodes linked by an all-undirected path are **equivalent**, and a maximal such set is a **chain component** — the building block a CPDAG uses to represent an entire equivalence class of DAGs at once [§sec_7].

A path between $X$ and $Y$ is **blocked** by a conditioning set $Z$ (excluding $X,Y$) if some node $m$ on it satisfies one of two conditions, and it is precisely this branching test that d-separation, and hence adjustment-set validity, is built on [§sec_7]:

```algorithm
title: Testing whether a path is blocked by Z
lines:
  - code: "for each interior node m on the path:"
    intent: "Blocking is a local property checked node by node, not a property of the path as a whole [§sec_7]"
  - code: "    if m is not a collider on this path and m in Z:"
    intent: "Conditioning on a chain or fork node cuts the dependence flowing through it [§sec_7]"
  - code: "        path is BLOCKED at m"
    intent: "One blocking node is enough to close the whole path [§sec_7]"
  - code: "    elif m is a collider on this path and m not in Z and no descendant of m in Z:"
    intent: "An un-conditioned collider already stops dependence from passing through [§sec_7]"
  - code: "        path is BLOCKED at m"
    intent: "Colliders block by default — the opposite behavior from every other node type [§sec_7]"
  - code: "if no interior node triggered either case: path is ACTIVE"
    intent: "A path only carries dependence if it survives every node's test [§sec_7]"
```

## The Math {#the-math}
The collider clause is the one that surprises: conditioning on $m$ or on any descendant of $m$ *removes* $m$ from the blocking set, turning a previously blocked path active. Concretely, on $X \to M \leftarrow Y$ the path is blocked with $Z=\emptyset$, but conditioning on $M$ (or on a child of $M$) opens it — $M$ becomes evidence linking $X$ and $Y$ even though neither causes the other. This is why the two cases in the algorithm above cannot be merged into one rule [§sec_7].

Two disjoint sets $A, B$ are **d-separated** by $Z$ if *every* path between them is blocked by $Z$ — a universal, not existential, quantifier over paths, which is what makes d-separation a strong enough condition to license conditional independence. A distribution $P$ is **Markov** with respect to $G$ if d-separation implies conditional independence, and **faithful** if the converse holds; together they force the graph's separations and the distribution's independencies to coincide exactly, which is the assumption SID leans on when it reads adjustment sets off graph structure [§sec_7].

Two DAGs are **Markov equivalent** exactly when they entail the same set of conditional independencies — equivalently, the same set of d-separations — and a whole equivalence class is summarized by one **CPDAG**, whose edges follow a three-way rule [§sec_7]:

| CPDAG edge | Condition across the equivalence class | Anchor |
|---|---|---|
| Directed $X \to Y$ | *every* member DAG has that edge, in that direction | [§sec_7] |
| Undirected $X - Y$ | some members orient it one way, others the opposite way | [§sec_7] |
| No edge | no member DAG connects $X$ and $Y$ | [§sec_7] |

This rule is why a CPDAG is strictly less informative than any single DAG in its class: every undirected edge is a place where the data alone cannot determine causal direction, and it is exactly these ambiguous edges that force SID to consider best- and worst-case orientations rather than a single distance value [§sec_7].

## Go Deeper {#go-deeper}
- **Structural Intervention Distance (SID)** — the prerequisite concept this terminology serves; read it next to see how ancestry, blocking, and CPDAG ambiguity feed directly into how SID scores an estimated graph against a true one.
