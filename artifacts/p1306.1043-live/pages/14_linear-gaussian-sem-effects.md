# Causal Effects in Linear Gaussian SEMs
## TL;DR {#tldr}
SID needs a way to check whether the adjustment set implied by an estimated graph actually recovers the true causal effect — and in a linear Gaussian structural equation model, that check has a closed-form answer instead of requiring simulation. Because every variable is a linear combination of its parents plus Gaussian noise, the whole joint distribution collapses to a single covariance matrix, and the causal effect of any intervention is just a number you read off that matrix. This is what lets SID compare "correct" versus "wrong" adjustment sets exactly, rather than approximately, and it's the computational building block the SID algorithms sit on top of.

## Intuition {#intuition}
If you intervene on a variable X in a linear Gaussian model, everything downstream shifts by an amount proportional to how hard you pushed X — there are no thresholds, no interactions, no curvature to worry about. That means the entire intervention effect can be summarized by a single slope: how much the mean of Y moves per unit change in X. The spread of Y around that shifted mean stays the same no matter how hard you intervene, because intervening on X only overwrites its own random source of variation, not the noise that separately perturbs Y.

The classical trick for computing that slope without touching the intervention distribution directly is to condition on the parents of X instead. Conditioning on X's parents closes off every non-causal ("backdoor") route between X and Y, so the ordinary conditional relationship between X and Y, once you've adjusted for those parents, equals the causal one. In a Gaussian world this adjustment is just linear regression, and linear regression coefficients are themselves expressible purely in terms of covariances — which is why the whole computation reduces to matrix algebra on the covariance matrix Σ.

## Mechanics {#mechanics}
The covariance matrix Σ of the full variable set is determined entirely by the structural coefficients (how strongly each variable depends on its parents) and the noise variances — nothing about the intervention itself is needed to compute it, since Σ describes the observational distribution the SEM already implies [§sec_11]. Once Σ is known, every causal effect in the graph can be read off it analytically rather than estimated from samples, which is what makes SID's comparisons between graphs exact rather than statistical [§sec_11].

The intervention distribution p(Y | do(X = x)) stays Gaussian, with a mean that moves linearly in x and a variance that does not depend on x at all — do(X = x) replaces X's own noise term, so it only ever shifts downstream means, never their spread [§sec_11]. This is exactly why a single scalar, the causal effect, can summarize the whole intervention distribution instead of needing the full conditional law [§sec_11].

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

**Why this is the causal effect and not just a correlation:** conditioning on PA(X) is a valid backdoor adjustment, since parents block every non-causal path into X by construction of the DAG, so the ordinary conditional mean E[Y | X=x, PA(X)=pa] already equals the interventional mean once averaged over the parents' distribution [§sec_11]. Under joint Gaussianity that conditional mean is exactly linear in (x, pa), so its coefficient on x is the standard multiple-regression slope, and the Frisch–Waugh–Lovell identity says that slope equals the ratio above: partial covariance of Y and X, divided by partial variance of X, both after removing PA(X)'s contribution [§sec_11].

**A worked example showing why the PA(X) term is not optional.** Take a four-variable chain with a confounder: W → X, W → Z, X → Z, Z → Y, with coefficients X = W + ε_X, Z = 0.5X + 0.3W + ε_Z, Y = 2Z + ε_Y, and all noise variances equal to 1 [§sec_11]. The true causal effect of X on Y runs only through Z, so it is 0.5 × 2 = 1.0 [§sec_11]. Propagating the structural equations gives Σ_{X,X}=2, Σ_{Y,X}=2.6, Σ_{W,X}=1, Σ_{Y,W}=1.6, Σ_{W,W}=1 [§sec_11].

- Naive slope with no adjustment: Σ_{Y,X} / Σ_{X,X} = 2.6 / 2 = 1.3 — inflated, because W confounds X and Y through the second path into Z [§sec_11].
- Adjusted via PA(X) = {W}: numerator = 2.6 − (1.6)(1)(1) = 1.0, denominator = 2 − (1)(1)(1) = 1.0, giving α = 1.0 — exactly the true effect [§sec_11].

The gap between 1.3 and 1.0 is the entire reason the formula subtracts the Σ_{·,PA(X)} terms rather than just taking a raw covariance ratio: skipping that term is precisely the error SID is built to detect when a candidate graph proposes the wrong parent set [§sec_11].

## Go Deeper {#go-deeper}
- §sec_11 of the paper — the source of the covariance-matrix construction and the causal-effect formula worked through above; read it directly for the SEM notation used elsewhere in the paper [§sec_11].
- SID Algorithms (downstream concept) — consumes exactly this closed-form causal effect as its correctness check when scoring an estimated graph's adjustment sets against the true DAG's.
