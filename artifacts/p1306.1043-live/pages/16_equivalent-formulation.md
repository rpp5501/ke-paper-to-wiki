# Equivalent Graphical Formulation
## TL;DR {#tldr}
SID starts out defined in terms of intervention distributions — asking whether a candidate adjustment set recovers the correct causal effect for every pair of variables. Checking that directly means reasoning about distributions, which is expensive and awkward to compute. This concept rewrites the same question as a purely graphical test: whether a candidate set blocks certain paths and avoids certain descendants in the true DAG. Nothing about *what* SID measures changes — only how you check it, which is what turns SID from a distributional definition into an algorithm you can actually run on graphs.

## Intuition {#intuition}
The original question was "does adjusting for this set give the right causal effect?" — which sounds like it requires comparing distributions under intervention versus observation. The insight here is that this question has a fixed, topological answer: whether a set is a valid adjustment set depends only on the shape of the graph — which nodes are descendants of which, and which paths get blocked — not on the particular numbers attached to the edges.

This also loosens what people usually assume about adjustment. It is not "you must recover the true parent set" — several other sets work just as well. You can adjust for children of a cause, as long as they don't sit on the directed path to the effect, or skip parents whose only route to the outcome runs back through the cause itself anyway. The graphical criterion accepts anything topologically equivalent to blocking the confounding while leaving the causal channel open.

## Mechanics {#mechanics}
**From distributions to one candidate set:** for each ordered pair $(i,j)$, the question the SID needs answered stops being "search over adjustment sets" and becomes a single yes/no check — whether $\PA{\HH}{i}$, the parent set from the *estimated* graph, is a valid adjustment set for the intervention on $i$ with respect to $j$ in the *true* graph $\G$ [§sec_2_2].

**Why one check suffices, and why it's tight:** a Lemma supplies a two-sided characterization built around a graphical condition, tagged (*). If a candidate set satisfies (*), it is guaranteed to be a valid adjustment set under every distribution Markov to $\G$; if it fails (*), there is always some Markov-compatible distribution for which it is *not* valid [§sec_2_2]. This two-sidedness is what licenses replacing "check across all distributions" with "check the graph once" — the graphical test isn't merely sufficient, it's exactly the boundary between valid and invalid.

**Consistency with the earlier definition:** when the candidate set is exactly the true parent set, $\B{Z} = \PA{\G}{i}$, condition (*) is satisfied automatically, and the Lemma collapses back to the earlier Proposition that parent-set adjustment always works [§sec_2_2].

**Relation to the classic criterion:** condition (*) is recognizable as a slight loosening of the standard back-door criterion, extended to also license certain non-parent sets as valid adjustments [§sec_2_2].

**Which non-parent sets qualify:** a child of the treatment can be a valid adjustment variable as long as it is not itself on the directed path from cause to effect, and a parent of the treatment can be dropped from the adjustment set if every unblocked path it would otherwise create is already forced through the treatment [§sec_2_2].

## The Math {#the-math}
The graphical condition (*) that a candidate set $\B{Z}$ must satisfy for the pair $(X,Y)$ is stated in two parts — a descendant restriction and a path-blocking requirement [eq_6].

$$
\left \{
\begin{array}{c}
\text{In } \G \text{, no } Z \in \B{Z} \text{ is a descendant of any } W \text{ which lies on a directed}\\
\text{path from } X \text{ to } Y \text{ and } \B{Z} \text{ blocks all non-directed paths from } X \text{ to } Y.
\end{array}
\right.
$$ [eq_6]

```annotated-eq
latex: "\\left \\{ \\begin{array}{c} \\text{In } \\G \\text{, no } Z \\in \\B{Z} \\text{ is a descendant of any } W \\text{ which lies on a directed} \\\\ \\text{path from } X \\text{ to } Y \\text{ and } \\B{Z} \\text{ blocks all non-directed paths from } X \\text{ to } Y. \\end{array} \\right."
terms:
  - tex: "Z \\in \\B{Z}"
    role: 1
    words: "Any member of the candidate adjustment set — the descendant restriction has to hold for every one of them, not just some [§sec_2_2]"
  - tex: "W"
    role: 2
    words: "A mediator on the directed path from X to Y; if an adjustment variable descends from one, conditioning on it reopens or biases the causal path instead of blocking a confounding one [§sec_2_2]"
  - tex: "\\text{blocks all non-directed paths}"
    role: 3
    words: "The other half of the requirement — this is the back-door-style piece that closes off spurious association while the descendant restriction protects the causal channel itself [§sec_2_2]"
```

Substituting $\B{Z} = \PA{\HH}{i}$ into (*) for every pair turns the whole distributional definition of SID into a graph-counting formula, splitting on whether $j$ is already a parent of $i$ in the estimated graph $\HH$ [eq_7].

$$
\SID(\G,\HH) = \# \left\{\,(i,j), i \neq j\,|\, 
\begin{array}{cl}
j \in \DE{\G}{i} & \text{if } j \in \PA{\HH}{i}\\
\PA{\HH}{i} \text{ does not satisfy } (*) \text{ for } (\G,i,j) & \text{if } j \not \in \PA{\HH}{i}
\end{array}
\right\}
$$ [eq_7]

**Why the case split exists:** when $\HH$ already claims $j$ as a parent of $i$, condition (*) is vacuous — the estimated graph has already committed to a causal claim rather than an adjustment question — so the check degenerates to the simpler test of whether $j$ is even a descendant of $i$ in the true graph $\G$; get the direction wrong there and the mismatch is counted regardless of any adjustment reasoning [eq_7]. When $j$ is not a claimed parent, the pair is scored by whether $\PA{\HH}{i}$, taken as the candidate adjustment set, satisfies (*) in $\G$ [eq_7].

**Where the tractability gain comes from:** the reformulation replaces a search over adjustment sets and a comparison of interventional distributions with a single descendant/blocking check per pair, against one fixed candidate set — $\PA{\HH}{i}$ — rather than an unbounded family of candidates [§sec_2_2].

## Go Deeper {#go-deeper}
- **Motivation and Definition of SID** — the distributional definition this formulation replaces; read it first to see exactly which computation (*) is standing in for.
- **Proof: Equivalence of Definitions** — the appendix proof, built on the same Lemma, that formally establishes eq_7 is identical to the original definition, not just a good approximation of it.
- **Metric Properties of SID** — builds on this graphical formulation to establish SID's properties as a distance; worth checking once you trust that (*) really characterizes valid adjustment.
