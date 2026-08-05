# SID between a CPDAG and a DAG or CPDAG
## TL;DR {#tldr}
When the true causal structure can only be identified up to a Markov equivalence class rather than as a single DAG, SID can still be defined — but only pairs whose intervention distribution is actually identifiable from that class are allowed to count as errors, and when the estimate is itself a CPDAG the score becomes a range rather than a single number.

## Intuition {#intuition}
Not every causal setting yields a unique ground-truth DAG. A linear Gaussian SEM with unequal error variances, for instance, only lets you recover the correct DAG's Markov equivalence class under faithfulness, not the DAG itself. Comparing an estimate against a single arbitrarily-chosen member of that class would be misleading, since different members disagree on some effects. The natural fix is to compare against the whole equivalence class at once, but only judge the estimate on effects that class actually pins down — effects the CPDAG leaves ambiguous simply aren't scored.

## Mechanics {#mechanics}
The core move is restricting the counted pairs to those where the intervention distribution is **identifiable** directly from the true CPDAG $\mathcal{C}$, rather than from one guessed member DAG. A pair $(i,j)$ only enters the comparison if some DAG $\mathcal{C}_1$ consistent with $\mathcal{C}$ gives an intervention distribution that can be checked against the estimate's — effects the equivalence class leaves ambiguous are excluded from scoring by construction [§sec_2_4_2].

Identifiability is decided by a purely graphical test on paths in the partially directed graph:
- A path is **possibly directed** from $i$ to $j$ if none of its edges point backward toward the node closer to $i$ — i.e., every edge is either undirected or oriented forward along the path [§sec_2_4_2].
- The intervention distribution from $i$ to $j$ is **not identifiable** in $\mathcal{C}$ if and only if such a possibly-directed path exists that starts with an undirected edge out of $i$ [§sec_2_4_2].
- This criterion comes from a generalized backdoor characterization of identifiability in CPDAGs, applied here purely as a graph test rather than requiring numerical checks on the SEM [§sec_2_4_2].

This gives four variants of the score, built up incrementally from the DAG-vs-DAG baseline:

| True structure | Estimated structure | How the score is computed | Anchor |
|---|---|---|---|
| DAG $G$ | DAG $H$ | Single exact value (baseline definition) | [§sec_2_4_2] |
| DAG $G$ | CPDAG $H$ | Lower/upper bounds over DAGs in $H$'s equivalence class | [§sec_2_4_2] |
| CPDAG $\mathcal{C}$ | DAG $H$ | Exact value, but restricted to pairs identifiable in $\mathcal{C}$ | [eq_10] |
| CPDAG $\mathcal{C}$ | CPDAG $H$ | Lower/upper bounds combining the identifiability restriction with enumeration over $H$'s equivalence class | [§sec_2_4_2] |

When $\mathcal{C}$ happens to be a fully-oriented DAG, every intervention distribution is trivially identifiable, so the four rows collapse: the last two rows reduce to the first two, and this construction is exactly the earlier DAG-vs-{DAG,CPDAG} definitions rather than a genuinely new object [§sec_2_4_2].

## The Math {#the-math}
The score is defined as a count over ordered node pairs, gated by an existential witness DAG drawn from the true CPDAG's equivalence class, which is introduced here [eq_10]:

$$\begin{array}{rcl}
\mathrm{SID}: \; \mathbb{C} \times \mathbb{G} &\rightarrow& \mathbb{N}\\
(\CC,\HH)& \mapsto &\# \{\,(i,j), i \neq j\;|\;\text{the interv. distr from $i$ to $j$ is identif. in $\CC$}\\
&& \qquad \qquad \qquad \quad \text{and } \exists \lawX \text{ that is Markov wrt } \CC_1 \in \CC \text{ such that}\\
&& \qquad \qquad \qquad \quad p_{\CC_1}(x_j\given \doo(X_i = \hat x_i)) \neq p_{\HH}(x_j\given \doo(X_i = \hat x_i)) \}
\end{array}$$ [eq_10]

```annotated-eq
latex: "\\mathrm{SID}(\\CC,\\HH) = \\#\\{(i,j), i \\neq j \\mid \\text{identif. in } \\CC \\text{ and } \\exists\\, \\CC_1 \\in \\CC:\\; p_{\\CC_1}(x_j \\mid \\doo(X_i=\\hat x_i)) \\neq p_{\\HH}(x_j \\mid \\doo(X_i=\\hat x_i))\\}"
terms:
  - tex: "\\mathrm{SID}(\\CC,\\HH)"
    role: 1
    words: "The map is defined on $\\mathbb{C} \\times \\mathbb{G}$, so the first argument is now allowed to be a CPDAG instead of a DAG [eq_10]"
  - tex: "\\text{identif. in } \\CC"
    role: 2
    words: "A gatekeeping clause absent from the DAG-only definition: pairs the equivalence class leaves ambiguous never enter the count at all [eq_10]"
  - tex: "\\exists\\, \\CC_1 \\in \\CC"
    role: 3
    words: "The comparison is delegated to one witness DAG consistent with $\\CC$, not to $\\CC$ directly, since $\\CC$ alone has no numerical intervention distribution [eq_10]"
  - tex: "p_{\\CC_1}(x_j \\mid \\doo(X_i=\\hat x_i))"
    role: 4
    words: "The ground-truth interventional value, well-defined once the identifiability gate has already guaranteed it does not depend on which consistent DAG was picked [eq_10]"
  - tex: "p_{\\HH}(x_j \\mid \\doo(X_i=\\hat x_i))"
    role: 5
    words: "The estimate's implied value, computed exactly as in the DAG-vs-DAG case since $\\HH$ here is a single DAG [eq_10]"
```

The identifiability gate is what makes the definition well-posed: without it, $p_{\CC_1}(x_j \mid \doo(X_i=\hat x_i))$ could differ across different $\CC_1 \in \CC$, making the "$\exists$" clause satisfiable by cherry-picking a convenient witness rather than reflecting a genuine disagreement with $\HH$ [eq_10]. The boundary case makes this concrete:

```derivation
shape: Reduce the CPDAG definition to the earlier DAG-only SID when the true structure has no undirected edges.
steps:
  - latex: "\\CC = \\{G\\},\\; G \\text{ fully oriented}"
    why: "A DAG has no undirected edges, so no possibly-directed path can start with one — every effect is identifiable in $\\CC$ [§sec_2_4_2]"
  - latex: "\\text{identif. in } \\CC \\equiv \\text{true for all } (i,j)"
    why: "The gating clause in eq_10 becomes vacuous, so it drops out of the count entirely [eq_10]"
  - latex: "\\exists\\, \\CC_1 \\in \\CC \\;\\equiv\\; \\CC_1 = G"
    why: "The equivalence class is the singleton $\\{G\\}$, so the existential witness is forced rather than chosen [eq_10]"
  - latex: "\\mathrm{SID}(\\CC,\\HH) = \\#\\{(i,j) : p_G(x_j\\mid \\doo(X_i=\\hat x_i)) \\neq p_{\\HH}(x_j\\mid \\doo(X_i=\\hat x_i))\\}"
    why: "This is exactly the DAG-vs-DAG definition, confirming the CPDAG extension is conservative rather than a different metric on the overlap of its domain [§sec_2_4_2]"
```

The extension to an estimated CPDAG $\HH$ (rather than a DAG) is not solved exactly for the same reason a DAG-vs-CPDAG comparison isn't: $\HH$ represents many candidate DAGs, so instead of one count the paper reports the lower and upper bound of the score across all DAGs consistent with $\HH$'s equivalence class, paying the cost of enumerating that class rather than evaluating a single closed-form count [§sec_2_4_2].

## Go Deeper {#go-deeper}
- **SID between a DAG and a CPDAG** (builds-on) — read this first: it supplies the lower/upper-bound machinery over an equivalence class that this concept reuses for the estimate side.
- The **generalized backdoor criterion** underlying the identifiability lemma cited here is worth tracing back to its source result, since the possibly-directed-path test used above is stated as a direct corollary of it rather than derived from scratch [§sec_2_4_2].
