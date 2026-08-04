# Equivalent Graphical Formulation

## TL;DR {#tldr}
The Structural Intervention Distance is hard to compute directly from its causal definition, so it can be rewritten as a purely graphical question: for each ordered pair of variables, does the parent set in the estimated graph act as a valid *adjustment set* for the intervention in the true graph? This reformulation turns SID from a statement about interventional distributions into something that can be checked by walking paths in a DAG.

## Intuition {#intuition}
Instead of asking "would intervening on X give the same effect on Y in both graphs?", the equivalent formulation asks "does the set of parents of X in the guessed graph do the job of a legitimate adjustment set in the true graph?" A valid adjustment set is not necessarily the parent set — children that aren't on a directed path to Y can work too, and some parents can be skipped if every unblocked path through them is already blocked elsewhere. This flexibility is what makes the graphical check richer than the naive backdoor criterion, while still being fully determined by graph structure rather than by any particular distribution.

## Mechanics {#mechanics}
The reformulation starts from the observation that the original causal definition of SID is difficult to compute, motivating a graph-only equivalent built around whether a given set is a valid adjustment set for an intervention [§sec_2_2]. A key lemma characterizes this: if a candidate set satisfies a specific structural property relative to the true DAG, then for every distribution Markov with respect to that DAG, the set is a valid adjustment set; conversely, if the property fails, there exists at least one Markov-compatible distribution for which the set is not valid [§sec_2_2]. When the candidate set is exactly the parent set of X, this property reduces to the ordinary backdoor criterion, showing the new condition is a genuine extension of it rather than something unrelated [§sec_2_2]. The extension explains why other sets besides the parents can serve as valid adjustments — for instance, children of X that are not themselves on a directed path from X to Y, or parents of X whose unblocked paths to Y are already blocked through other members of the set [§sec_2_2].

## The Math {#the-math}
The graphical property (*) that a candidate set must satisfy is stated as: no member of the set may be a descendant of any node lying on a directed path from X to Y, and the set must block every non-directed path from X to Y [eq_6].

$$
\left \{
\begin{array}{c}
\text{In } \G \text{, no } Z \in \B{Z} \text{ is a descendant of any } W \text{ which lies on a directed}\\
\text{path from } X \text{ to } Y \text{ and } \B{Z} \text{ blocks all non-directed paths from } X \text{ to } Y.
\end{array}
\right.
$$ [eq_6]

Using this criterion, SID itself is rewritten entirely in graph-theoretic terms: for each ordered pair (i, j) with i ≠ j, the pair is counted as an error either if j is not a descendant of i in the true graph while j is a parent of i in the estimated graph, or if j is not a parent of i in the estimated graph but the estimated parent set of i fails to satisfy (*) for the true graph and the pair (i, j) [eq_7].

$$
\SID(\G,\HH) = \# \left\{\,(i,j), i \neq j\,|\,
\begin{array}{cl}
j \in \DE{\G}{i} & \text{if } j \in \PA{\HH}{i}\\
\PA{\HH}{i} \text{ does not satisfy } (*) \text{ for } (\G,i,j) & \text{if } j \not \in \PA{\HH}{i}
\end{array}
\right\}
$$ [eq_7]

This formulation is what later gets exploited for actual computation of SID, since checking (*) is a graph traversal problem rather than one requiring reasoning about distributions [§sec_2_2].

## Go Deeper {#go-deeper}
No research note is attached to this concept, so there are no additional resources to list here.
