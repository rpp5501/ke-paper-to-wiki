# SID between a CPDAG and a DAG or CPDAG
## TL;DR {#tldr}
Some estimation procedures never recover a single causal DAG — only the Markov equivalence class it belongs to, represented as a CPDAG. SID between a DAG and a CPDAG already lets you score an estimated CPDAG against a known true DAG; this concept flips that around and extends it further, so the *true* structure can also be a CPDAG on either side of the comparison. The score now has to account for the fact that a CPDAG bundles many DAGs together, some of which disagree with each other about a given intervention effect.

## Intuition {#intuition}
If the ground truth itself is only identifiable up to an equivalence class, it's not meaningful to grade an estimate against one arbitrarily chosen DAG from that class — different members would give different, equally "correct," verdicts. The natural fix is to score against the whole class at once, but only on the questions the class can actually answer.

That means restricting attention to intervention effects that are identifiable from the CPDAG itself, regardless of which member DAG happens to be the true one. Effects that aren't identifiable are simply not counted as either right or wrong, since the true CPDAG makes no unambiguous claim about them.

## Mechanics {#mechanics}
**Why a CPDAG can be the correct target at all:** simulating from a linear Gaussian SEM with different error variances is a case where the joint distribution can't pin down the true DAG, but under a faithfulness assumption it can still pin down the correct Markov equivalence class. In that situation the natural comparison is between the estimated structure and the true CPDAG, not a true DAG that isn't even identifiable [§sec_2_4_2].

**The restriction that makes this well-defined:** a CPDAG $\mathcal{C}$ represents an equivalence class of DAGs $\mathcal{C}_1, \mathcal{C}_2, \dots$, and these different DAGs can disagree on the intervention distribution from $i$ to $j$. Rather than pick one, SID only ever asks about pairs $(i,j)$ whose intervention distribution is identifiable in $\mathcal{C}$ — i.e., every DAG consistent with $\mathcal{C}$ agrees on it — using a generalized backdoor criterion to characterize identifiability [§sec_2_4_2].

**The graphical shortcut for identifiability:** a path in a partially directed graph is called *possibly directed* if none of its edges points backward against the direction of travel from $i$ to $j$. The identifiability criterion is then purely graphical: the intervention distribution from $i$ to $j$ is *not* identifiable in $\mathcal{C}$ exactly when there is a possibly directed path from $i$ to $j$ that starts with an undirected edge — an unresolved edge right at the source is enough to let different member DAGs send the effect through different routes [§sec_2_4_2].

**Why the DAG case falls out for free:** when $\mathcal{C}$ is itself a DAG, it has only one member, so every intervention distribution is trivially identifiable and the possibly-directed-path condition never triggers. The CPDAG definitions then collapse exactly onto the earlier DAG-to-DAG and DAG-to-CPDAG definitions, so this is a genuine generalization rather than a parallel, incompatible definition [§sec_2_4_2].

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

**Why bounds reappear for the CPDAG-vs-CPDAG case:** when the estimate $\mathcal{H}$ is itself a CPDAG rather than a DAG, the extension is completely analogous, but now both sides bundle multiple DAGs, so a single count is no longer well-defined; the result is reported as lower and upper bounds over all DAGs consistent with the estimated equivalence class, mirroring how the DAG-vs-CPDAG case was already handled [§sec_2_4_2].

## Go Deeper {#go-deeper}
- **SID between a DAG and a CPDAG** — the direct prerequisite: this concept only generalizes that definition by letting the *true* side also be a CPDAG, so its identifiability machinery and bound structure carry over unchanged.
- **Generalized backdoor criterion (Corollary 4.2)** — the identifiability result this section's graphical lemma is derived from; worth reading directly for the proof behind the "possibly directed path starting undirected" criterion, which is only stated here, not derived.
