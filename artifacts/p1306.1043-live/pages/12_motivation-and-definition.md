# Motivation and Definition of SID

## TL;DR {#tldr}
SID is a directed pre-metric between DAGs that counts how many ordered pairs of variables get the wrong interventional prediction when the true graph is replaced by an estimate — it scores a graph by how well it supports *do*-calculus, not by how many edges it got wrong.

## Intuition {#intuition}
Two candidate graphs can sit at the exact same edge-distance from the truth and still behave completely differently once you start asking "what happens if I intervene here?" One might add a spurious edge that turns out to be harmless, because the extra variable it makes you adjust for doesn't actually change the computed distribution. Another might reverse a single edge and, in doing so, silently drop the one confounder every downstream prediction depended on. SID is built to tell these two mistakes apart, since it evaluates a graph by the correctness of the intervention distributions it implies, which is exactly what the SID class and its underlying pair-checking routine compute.

## Mechanics {#mechanics}
The motivating example fixes a true DAG $G$ and two estimates that are each exactly one edge away from $G$, so they are indistinguishable by SHD. $H_1$ adds an edge $Z_1 \to Z_2$; $H_2$ reverses the edge between $X$ and $Y$. Parent-adjustment is used throughout to compute intervention distributions from either graph's structure [§sec_2_1].

| Estimate | Structural change from $G$ | SHD | Intervention pairs broken |
|---|---|---|---|
| $H_1$ | adds $Z_1 \to Z_2$ | 1 | none — $Z_2$ gains an extra adjustment variable that cancels out [eq_4] |
| $H_2$ | reverses $X \to Y$ to $Y \to X$ | 1 | eight ordered pairs, because $X$ loses its only parent and the adjustment set needed for $\text{do}(X)$ disappears [§sec_2_1] |

The reason $H_1$ escapes unpunished is structural: every node except $Z_2$ keeps the same parent set in $G$ and $H_1$, so parent adjustment produces literally the same formula for those nodes. $Z_2$'s adjustment set grows by one variable, $Z_1$, but $Z_1$ turns out to be conditionally screened off once $X, Z_2$'s true parents, are already in the set, so the extra term drops out algebraically rather than by luck [§sec_2_1].

$H_2$ fails for a different reason: computing $\text{do}(X)$ correctly requires adjusting for $Y$, the confounder linking $X$ to $Z_1, Z_2, Z_3$ through the true edge $X \to Y$. In $H_2$, $X$ has no parents at all, so parent adjustment conditions on nothing, and the resulting distribution is generically wrong for every target reachable from $X$ [§sec_2_1].

An ordered pair $(i,j)$ is classified by comparing $p_H(\cdot \mid \text{do}(X_i=x_i))$ against $p_G(\cdot \mid \text{do}(X_i=x_i))$ for **every** distribution Markov with respect to $G$, not just one observational sample — a single fully-independent distribution would make almost any two graphs agree, so the definition quantifies over the whole Markov-compatible family to stay purely graphical [§sec_2_1].

## The Math {#the-math}
The $H_1$ case generalizes to the following identity, using $Y_1,Y_2,Y_3$ for a directed chain and $X_1,X_2$ for the true parents of $Y_2$ that $H_1$ shares with $G$ plus the spurious extra parent $Y_1$ [eq_4]:

$$
\begin{aligned}
p_{\HH_1}(y_3\given \doo(Y_2 = \hat y_2)) &= \sum_{x_1,x_2,y_1} p(y_3\given x_1,x_2,y_1,\hat y_2) p(x_1,x_2,y_1)\\
& = \sum_{x_1,x_2,y_1} \frac{p(x_1,x_2,y_1,\hat y_2,y_3)}{p(\hat y_2 \given x_1,x_2,y_1)}
 = \sum_{x_1,x_2,y_1} \frac{p(x_1,x_2,y_1,\hat y_2,y_3)}{p(\hat y_2 \given x_1,x_2)}\\
& = \sum_{x_1,x_2} p(y_3\given x_1,x_2,\hat y_2) p(x_1,x_2)
 = p_{\G}(y_3\given \doo(Y_2 = \hat y_2))
\end{aligned}
$$ [eq_4]

```derivation
shape: Show H1's spurious extra parent cancels out of the intervention formula.
steps:
  - latex: "p_{H_1}(y_3 \\mid do(Y_2=\\hat y_2)) = \\sum_{x_1,x_2,y_1} p(y_3\\mid x_1,x_2,y_1,\\hat y_2)\\,p(x_1,x_2,y_1)"
    why: "Parent adjustment in H1 sums over ALL of Y2's H1-parents, which is X1, X2, and the spurious Y1 [eq_4]"
  - latex: "= \\sum_{x_1,x_2,y_1} \\frac{p(x_1,x_2,y_1,\\hat y_2,y_3)}{p(\\hat y_2\\mid x_1,x_2,y_1)} = \\sum_{x_1,x_2,y_1} \\frac{p(x_1,x_2,y_1,\\hat y_2,y_3)}{p(\\hat y_2\\mid x_1,x_2)}"
    why: "Rewriting as joint over conditional exposes the denominator, which collapses to p(y2|x1,x2) because Y1 is not a true parent of Y2 under G — the Markov property removes it [eq_4]"
  - latex: "= \\sum_{x_1,x_2} p(y_3\\mid x_1,x_2,\\hat y_2)\\,p(x_1,x_2) = p_{G}(y_3\\mid do(Y_2=\\hat y_2))"
    why: "Summing y1 out of the numerator reconstructs the plain joint over X1,X2,y2,y3, which is exactly G's parent-adjustment formula for Y2's true parent set {X1,X2} [eq_4]"
```

The definition that this example motivates treats SID as a map from pairs of DAGs to a count of failures, quantified over the full Markov-equivalent family rather than one distribution [eq_5]:

$$
\begin{array}{rcl}
\mathrm{SID}: \; \mathbb{G} \times \mathbb{G} &\rightarrow& \mathbb{N}\\
(\G,\HH)& \mapsto &\# \{\,(i,j), i \neq j\;|\;\text{ the intervention distribution from } i \text{ to } j\\
&& \qquad \qquad \qquad \quad \text{ is falsely estimated by } \HH \text{ with respect to } \G \}
\end{array}
$$ [eq_5]

```annotated-eq
latex: "\\mathrm{SID}(G,H) = \\#\\{(i,j) : i \\neq j,\\ p_H(x_j \\mid do(x_i)) \\neq p_G(x_j \\mid do(x_i)) \\text{ for some } p \\text{ Markov to } G\\}"
terms:
  - tex: "\\mathrm{SID}(G,H)"
    role: 1
    words: "Directed and non-symmetric by construction — swapping G and H changes which parent sets are used for adjustment, so SID(G,H) and SID(H,G) generally differ [eq_5]"
  - tex: "G"
    role: 2
    words: "Ground truth: fixes the space of observational distributions the count is quantified over, and supplies the correct intervention distributions [§sec_2_1]"
  - tex: "H"
    role: 3
    words: "Estimate under test: its structure supplies the parent sets that parent-adjustment plugs in to approximate G's intervention distributions [§sec_2_1]"
  - tex: "i \\neq j"
    role: 4
    words: "Only ordered, non-reflexive pairs are counted — there are n(n-1) of them for n variables, giving SID an integer range up to that bound [eq_5]"
```

The definition becomes executable by turning "falsely estimated" into a boolean per ordered pair: `SID` sums the boolean matrix that `_sid_matrix` produces, one True cell per pair whose intervention distribution eq_5 marks as incorrect [sid.py:L256]. `_sid_matrix` answers this per-source by checking, for every target, whether $H$'s parent set of the source is a valid back-door adjustment set in $G$ — the same two-condition check that eq_4's cancellation argument and $H_2$'s confounder-loss argument are instances of [sid.py:L183].

## Go Deeper {#go-deeper}
- **Equivalent Graphical Formulation** (builds-on) — turns this distribution-quantified definition into a criterion checkable purely from graph structure, without touching probability at all.
- **Alternative Adjustment Sets** (builds-on) — examines what happens to the definition if parent adjustment is swapped for a different valid adjustment set.
- **SID class** (`sid.py:L256`, implements) — the concrete metric object that runs this definition end to end on a pair of `DAG`s.
- **`_sid_matrix()`** (`sid.py:L183`, implements) — the per-pair reachability computation that eq_5's counting operation is actually built from.
- **Structural Intervention Distance (SID)** (part-of) — the parent topic covering SID's full property set beyond just this motivating definition.
