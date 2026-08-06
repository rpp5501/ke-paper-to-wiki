# SID between a CPDAG and a DAG or CPDAG
## TL;DR {#tldr}
Some estimators recover only a CPDAG: a Markov equivalence class rather than one causal DAG.

Earlier SID scores an estimated CPDAG against known DAG truth. This extension also allows the true structure, or both structures, to be CPDAGs.

The score must account for member DAGs that disagree about an intervention effect.

## Intuition {#intuition}
When truth is only an equivalence class, grading against one arbitrary member DAG is meaningless. Different members can give different yet equally valid verdicts.

SID instead scores the whole class, but only on questions it can answer.

SID considers intervention effects identifiable from the CPDAG, regardless of which member DAG is true.

Non-identifiable effects are neither right nor wrong because the CPDAG makes no unambiguous claim about them.

**Worked example:** in CPDAG $A-B-C$, the possibly directed path from $A$ to $C$ begins with an undirected edge. The effect is therefore excluded as non-identifiable rather than automatically counted wrong [§sec_2_4_2].

## Mechanics {#mechanics}
**Why a CPDAG can be the target:** a linear Gaussian SEM with different error variances need not identify its true DAG [§sec_2_4_2].

Under faithfulness, its joint distribution can still identify the correct Markov equivalence class. The natural target is therefore the true CPDAG [§sec_2_4_2].

**The well-defined restriction:** member DAGs $\mathcal{C}_1,\mathcal{C}_2,\dots$ can disagree on the $i$-to-$j$ intervention distribution [§sec_2_4_2].

SID scores only pairs identifiable in $\mathcal{C}$: every consistent DAG agrees on their effect. A generalized backdoor criterion characterizes that property [§sec_2_4_2].

**The graphical shortcut:** a path is *possibly directed* when no edge points backward while traveling from $i$ to $j$ [§sec_2_4_2].

The effect is not identifiable exactly when a possibly directed $i$-to-$j$ path begins with an undirected edge. That unresolved source edge lets member DAGs route the effect differently [§sec_2_4_2].

**Why the DAG case falls out for free:** a DAG-valued $\mathcal{C}$ has one member, so every intervention distribution is identifiable [§sec_2_4_2].

The possibly-directed-path condition never triggers. These definitions collapse to earlier DAG-to-DAG and DAG-to-CPDAG SID [§sec_2_4_2].

## The Math {#the-math}
The full definition scores a pair $(i,j)$ only when it is identifiable in $\mathcal{C}$, and then counts it as an error if *some* DAG $\mathcal{C}_1$ consistent with $\mathcal{C}$ disagrees with the estimate $\mathcal{H}$ on that intervention distribution [eq_10]:

$$
\begin{array}{rcl}
\mathrm{SID}: \; \mathbb{C} \times \mathbb{G} &\rightarrow& \mathbb{N}\\
(\CC,\HH)& \mapsto &\# \{\,(i,j), i \neq j\;|\;\text{the interv. distr from $i$ to $j$ is identif. in $\CC$}\\
&& \qquad \qquad \qquad \quad \text{and } \exists \lawX \text{ that is Markov wrt } \CC_1 \in \CC \text{ such that}\\
&& \qquad \qquad \qquad \quad p_{\CC_1}(x_j\given \doo(X_i = \hat x_i)) \neq p_{\HH}(x_j\given \doo(X_i = \hat x_i)) \}
\end{array}
$$ [eq_10]

```annotated-eq
latex: "\\mathrm{SID}(\\mathcal{C},\\mathcal{H}) = \\#\\{(i,j) : \\text{identif. in } \\mathcal{C} \\text{ and } \\exists\\, \\mathcal{C}_1 \\in \\mathcal{C},\\; p_{\\mathcal{C}_1}(x_j\\mid do(X_i=\\hat x_i)) \\neq p_{\\mathcal{H}}(x_j\\mid do(X_i=\\hat x_i))\\}"
terms:
  - tex: "\\mathbb{C} \\times \\mathbb{G} \\rightarrow \\mathbb{N}"
    role: 1
    words: "The domain is a true CPDAG paired with an estimated graph H (DAG or CPDAG) — the same codomain (a natural-number count) as the DAG-vs-CPDAG case it extends [eq_10]."
  - tex: "\\text{identif. in } \\CC"
    role: 2
    words: "A gatekeeper: pairs (i,j) whose effect isn't pinned down by every DAG in the class are excluded entirely, not scored as errors by default [§sec_2_4_2]."
  - tex: "\\exists\\, \\CC_1 \\in \\mathcal{C}"
    role: 3
    words: "It suffices that ONE member DAG of the true equivalence class disagrees with H — since identifiability already guarantees all members would agree with each other [eq_10]."
  - tex: "p_{\\CC_1}(x_j\\mid \\doo(X_i=\\hat x_i)) \\neq p_{\\HH}(\\cdot)"
    role: 4
    words: "The actual mismatch being counted: the true interventional distribution under the equivalence class versus the one implied by the estimate [eq_10]."
```

**Why CPDAG-vs-CPDAG needs bounds:** both sides now bundle multiple DAGs, so one count is not well-defined [§sec_2_4_2].

SID reports lower and upper bounds over DAGs consistent with the estimate, as in the DAG-to-CPDAG case [§sec_2_4_2].

## Go Deeper {#go-deeper}
- **SID between a DAG and a CPDAG** — the direct prerequisite: this concept only generalizes that definition by letting the *true* side also be a CPDAG, so its identifiability machinery and bound structure carry over unchanged.
- **Generalized backdoor criterion (Corollary 4.2)** — the identifiability result this section's graphical lemma is derived from; worth reading directly for the proof behind the "possibly directed path starting undirected" criterion, which is only stated here, not derived.
