# Metric Properties of SID

## TL;DR {#tldr}
SID is a *pre-metric*: it is zero exactly when the estimate makes no causal-prediction mistakes, and non-negative otherwise — but it is asymmetric and does not obey the triangle inequality. Knowing this keeps you from misreading its numbers.

## Intuition {#intuition}
SID answers "how bad is $\mathcal{H}$ as an estimate of $\mathcal{G}$?" That question is directional: mistaking a sparse graph for a dense one is not the same error as the reverse. So $\operatorname{SID}(\mathcal{G},\mathcal{H})$ and $\operatorname{SID}(\mathcal{H},\mathcal{G})$ can differ, and that asymmetry is a feature, not a bug — it mirrors the asymmetry of estimation.

The flip side: because it is not a true metric, you cannot chain SID values with a triangle inequality or treat them as distances in a geometric space.

## Mechanics {#mechanics}
SID is non-negative and equals zero when every ordered pair's estimated adjustment stays valid in the truth — notably, an estimate with *extra* edges can still score zero if those edges never invalidate an adjustment [§sec_2_3].

It is generally asymmetric, and the paper shows the triangle inequality can fail, so SID is classified as a pre-metric rather than a metric [§sec_2_3].

## The Math {#the-math}
Writing $p$ for the number of nodes, SID takes integer values in

$$ 0 \le \operatorname{SID}(\mathcal{G}, \mathcal{H}) \le p(p-1), $$

with $\operatorname{SID}(\mathcal{G}, \mathcal{H}) = 0$ iff no ordered pair violates the validity criterion. In general

$$ \operatorname{SID}(\mathcal{G}, \mathcal{H}) \neq \operatorname{SID}(\mathcal{H}, \mathcal{G}), $$

which is why a symmetrized variant is offered for comparing two graphs on equal footing [§sec_2_3].

## Go Deeper {#go-deeper}
- Symmetrized SID sums both directions when neither graph is "the estimate."
- The zero-with-extra-edges case motivates an edge-penalizing variant [§sec_2_4_3].
