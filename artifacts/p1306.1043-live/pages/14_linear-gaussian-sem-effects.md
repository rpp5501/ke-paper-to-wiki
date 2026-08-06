# Causal Effects in Linear Gaussian SEMs
## TL;DR {#tldr}
In a linear Gaussian SEM, SID can test an estimated adjustment set with a closed-form causal effect instead of simulation.

Each variable is a linear combination of its parents and Gaussian noise. The joint distribution becomes one covariance matrix, and each intervention effect is a number derived from it.

SID can therefore compare adjustment sets exactly. This is the computational building block for its algorithms.

## Intuition {#intuition}
In a linear Gaussian model, an intervention on $X$ shifts each downstream mean proportionally to the change in $X$. There are no thresholds, interactions, or curvature.

One slope summarizes the intervention effect: the mean change in $Y$ per unit change in $X$. $Y$'s variance stays fixed because the intervention replaces only $X$'s own noise source.

To compute the slope without an intervention distribution, condition on $X$'s parents. They close every non-causal backdoor route between $X$ and $Y$.

In a Gaussian model, that adjustment is linear regression. Its coefficients are covariance expressions, so the computation is matrix algebra on $\Sigma$.

## Mechanics {#mechanics}
The full covariance matrix $\Sigma$ is determined by structural coefficients and noise variances. It describes the SEM's observational distribution, so no particular intervention is needed to compute it [§sec_11].

Once $\Sigma$ is known, every causal effect is analytic rather than sample-estimated. SID's graph comparisons are therefore exact, not statistical [§sec_11].

The intervention distribution $p(Y \mid do(X=x))$ stays Gaussian. Its mean moves linearly in $x$, while its variance does not depend on $x$ [§sec_11].

$do(X=x)$ replaces $X$'s noise term and shifts downstream means without changing their spread. One causal-effect scalar can summarize the distribution [§sec_11].

```algorithm
title: Computing the causal effect of X on Y in a linear Gaussian SEM
lines:
  - code: "Sigma = cov(all variables)"
    intent: "computed once from the structural coefficients and noise variances, independent of any particular intervention [§sec_11]"
  - code: "S = PA(X)"
    intent: "the parents of X in the graph form a valid adjustment set — conditioning on them blocks every backdoor path out of X [§sec_11]"
  - code: "num = Sigma[Y,X] - Sigma[Y,S] @ inv(Sigma[S,S]) @ Sigma[S,X]"
    intent: "the part of the Y-X covariance left over after removing what PA(X) already explains about both [§sec_11]"
  - code: "den = Sigma[X,X] - Sigma[X,S] @ inv(Sigma[S,S]) @ Sigma[S,X]"
    intent: "the residual variance of X once PA(X) is partialled out — the only variance an intervention on X actually contributes [§sec_11]"
  - code: "alpha = num / den"
    intent: "the slope of the intervention distribution's mean in x, i.e. the causal effect SID will compare against the true DAG's value [§sec_11]"
```

## The Math {#the-math}
Writing Σ_{A,B} for the submatrix of Σ with rows indexed by set A and columns by set B, the causal effect is the population regression coefficient of Y on X after partialling out PA(X) [§sec_11]:

```annotated-eq
latex: "\\alpha_{Y,X} = \\frac{\\Sigma_{Y,X} - \\Sigma_{Y,\\mathrm{PA}(X)}\\,\\Sigma_{\\mathrm{PA}(X),\\mathrm{PA}(X)}^{-1}\\,\\Sigma_{\\mathrm{PA}(X),X}}{\\Sigma_{X,X} - \\Sigma_{X,\\mathrm{PA}(X)}\\,\\Sigma_{\\mathrm{PA}(X),\\mathrm{PA}(X)}^{-1}\\,\\Sigma_{\\mathrm{PA}(X),X}}"
terms:
  - tex: "\\alpha_{Y,X}"
    role: 1
    words: "The causal effect itself — the slope of E[Y | do(X=x)] in x, the number SID actually compares across graphs [§sec_11]"
  - tex: "\\Sigma_{Y,X} , \\Sigma_{X,X}"
    role: 2
    words: "Raw covariance and variance — what you'd use for the effect if X had no parents to confound with [§sec_11]"
  - tex: "\\Sigma_{Y,\\mathrm{PA}(X)},\\ \\Sigma_{X,\\mathrm{PA}(X)}"
    role: 3
    words: "How much of X and of Y is explained by X's parents — the confounding path that has to be subtracted out [§sec_11]"
  - tex: "\\Sigma_{\\mathrm{PA}(X),\\mathrm{PA}(X)}^{-1}"
    role: 4
    words: "Inverts the parents' own covariance so their shared contribution can be removed without double-counting correlated parents [§sec_11]"
```

**Why this is causal rather than correlational:** conditioning on $\mathrm{PA}(X)$ is valid backdoor adjustment, so the conditional mean equals the interventional mean after averaging over the parents [§sec_11].

Joint Gaussianity makes that conditional mean linear in $(x,pa)$. Its $x$ coefficient is the multiple-regression slope [§sec_11].

The Frisch-Waugh-Lovell identity makes this slope the displayed partial covariance divided by partial variance, after removing $\mathrm{PA}(X)$'s contribution [§sec_11].

**Worked example: why the $\mathrm{PA}(X)$ term is necessary.** Take $W \to X$, $W \to Z$, $X \to Z$, and $Z \to Y$, with $X=W+\epsilon_X$, $Z=0.5X+0.3W+\epsilon_Z$, and $Y=2Z+\epsilon_Y$ [§sec_11].

All noise variances are 1. The causal $X$-to-$Y$ effect runs through $Z$, so it is $0.5\times2=1.0$ [§sec_11].

The structural equations give $\Sigma_{X,X}=2$, $\Sigma_{Y,X}=2.6$, $\Sigma_{W,X}=1$, $\Sigma_{Y,W}=1.6$, and $\Sigma_{W,W}=1$ [§sec_11].

- Naive slope with no adjustment: Σ_{Y,X} / Σ_{X,X} = 2.6 / 2 = 1.3 — inflated, because W confounds X and Y through the second path into Z [§sec_11].
- Adjusted via PA(X) = {W}: numerator = 2.6 − (1.6)(1)(1) = 1.0, denominator = 2 − (1)(1)(1) = 1.0, giving α = 1.0 — exactly the true effect [§sec_11].

The gap between 1.3 and 1.0 is why the formula subtracts $\Sigma_{\cdot,\mathrm{PA}(X)}$ terms rather than using a raw covariance ratio [§sec_11].

Skipping that term is the kind of wrong-parent-set error SID detects [§sec_11].

## Go Deeper {#go-deeper}
- §sec_11 of the paper — the source of the covariance-matrix construction and the causal-effect formula worked through above; read it directly for the SEM notation used elsewhere in the paper [§sec_11].
- SID Algorithms (downstream concept) — consumes exactly this closed-form causal effect as its correctness check when scoring an estimated graph's adjustment sets against the true DAG's.
