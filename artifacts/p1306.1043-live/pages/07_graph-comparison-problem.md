# Comparing Estimated and True Causal Graphs

## TL;DR {#tldr}

An estimated DAG is useful only if it predicts intervention effects correctly. Matching the true graph edge-for-edge is not the real goal.

For each ordered variable pair, ask whether the estimate gives the same intervention prediction as the true graph. SID formalizes that question.

## Intuition {#intuition}

Two estimates can have equally many wrong edges but very different causal consequences. An error near a confounder can corrupt many intervention predictions; another error may change none.

| Metric | What it asks | What it can miss |
|---|---|---|
| Structural Hamming Distance | How many edges differ? | Whether those errors change intervention conclusions |
| SID | Does each ordered intervention prediction still work? | The edge count itself |

SID checks the estimated parent structure against the true intervention result for every ordered pair. Its score measures how much causal usefulness survived.

### Running four-node example

Keep this pair in view throughout the five chapters:

- true graph $G$: $A\to B$, $A\to C$, $B\to D$, and $C\to D$;
- estimate $H$: all edges in $G$, plus the extra edge $B\to C$.

The two graphs differ by one insertion, so their SHD is one. Yet $G\subseteq H$, making every parent set in $H$ a safe superset adjustment set for truth $G$ [§sec_2_3].

**Prediction check:** before calculating anything, decide whether that single structural error must create an intervention error. Chapter 3 will verify that $\mathrm{SID}(G,H)=0$, while swapping truth and estimate gives $\mathrm{SID}(H,G)=2$ [§sec_2_3; sid.py:L183-L253].

## Mechanics {#mechanics}

The setup distinguishes three objects [§sec_1]:

- a finite family of variables indexed by a vertex set;
- a joint distribution, its densities, and conditional densities with respect to Lebesgue or counting measure; and
- a graph of nodes and edges whose nodes are identified with those variables.

The identification lets one object serve as both a DAG vertex and a variable whose distribution can be conditioned on or intervened upon [§sec_1].

An estimate gets a vertex pair right when it predicts that pair's intervention distribution for every distribution Markov to the true graph [§sec_1].

Using the true graph's Markov class keeps the target fixed. The meaning of correctness cannot change with the estimate being scored [§sec_1].

This produces a genuinely new pre-distance between DAGs rather than a variant of SHD, and the paper is explicit that it is not aware of a directly related prior notion — it is meant to supplement SHD with information about causal-inference capacity, not replace it [§sec_1].

## The Math {#the-math}

**The core object is an ordered intervention question:** for each $i \neq j$, ask whether an estimate preserves the distribution of target $X_j$ after intervening on source $X_i$. With $p$ variables there are $p(p-1)$ such questions, which is the comparison space SID formalizes later [§sec_1].

**Why the formalism separates variables from densities:** the notation separately names the indexed variables, their joint distribution, and their conditional densities [§sec_1].

SID compares conditional and interventional densities. The notation must express the density of one variable after an intervention on another [§sec_1].

**What the node-variable identification buys:** an edge can be read as both a structural claim and a claim about conditional independence or intervention effects [§sec_1].

Without that convention, every graph-relative intervention definition would need an explicit map from vertices to variables [§sec_1].

**Boundary condition worth noting:** existence of the densities is assumed rather than derived, which quietly restricts the results that follow to distributions absolutely continuous with respect to Lebesgue or counting measure — discrete or continuous, but not, e.g., distributions with a singular component [§sec_1].

## Go Deeper {#go-deeper}

- **§sec_2 (Structural Hamming Distance)** — the baseline metric this concept is defined in contrast to; read it first to see exactly what "counting wrong edges" misses [§sec_1].
- **§sec_3 (do-calculus)** — supplies the machinery for the intervention distributions that SID actually compares, referenced here as prerequisite background [§sec_1].
- **§sec_4 (SID definition and properties)** — where the pairwise-correctness counting sketched above is turned into the formal (pre-)distance [§sec_1].
- **Appendix (DAG terminology)** — the graph-theoretic definitions the paper leans on throughout, flagged in the introduction as required background [§sec_1].
