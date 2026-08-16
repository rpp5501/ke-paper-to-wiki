# Conserved Quantities for Convergence and Parameterization
## TL;DR {#tldr}

Conserved quantities stay fixed along gradient flow, so any property that holds at initialization holds forever. That single fact does two jobs: it keeps convergence proofs tractable, and it labels which minimum a trajectory can reach.

## Intuition {#intuition}

Think of gradient flow as a ball rolling on a curved surface that has an exact symmetry — the surface looks the same after some translation, scaling, or rescaling of the parameters. That symmetry pins down a quantity the ball's motion cannot change, the way angular momentum stays fixed for a symmetric potential [S1].

The ball is not free to explore the whole surface. It is confined to a lower-dimensional slice fixed by its starting conserved-quantity value, and different starting slices can lead to different-shaped minima, some flatter than others [S1].

Because the slice is set at the very first step, the initialization already decides part of the outcome — before a single gradient update has run. Distill's visualizations of momentum trajectories on curved surfaces build the same intuition for how an invariant constrains a path, ahead of the formal argument here [S2].

## Mechanics {#mechanics}

The paper's argument for using conserved quantities in convergence analysis is a persistence claim: any condition stated purely in terms of a conserved quantity, if true at initialization, remains true for the entire gradient flow, because the quantity itself never moves [§sec_5_2].

Several existing convergence results for deep linear networks lean on exactly this persistence, each in a different way:

- Some convergence bounds require only that the imbalance stay invariant along the flow [§sec_5_2].
- Others assume the imbalance is small throughout training [§sec_5_2].
- Others assume it is exactly zero, the strongest case [§sec_5_2].
- A related result treats zero imbalance as the condition under which a linear network's gradient flow becomes a Riemannian gradient flow on the manifold of fixed-rank matrices [§sec_5_2].

Beyond stability, conserved quantities act as coordinates for the dynamics: because a quantity is constant along one trajectory, its value labels that trajectory, and its limiting value locates where the trajectory ends up within the set of minima [§sec_5_2].

This labeling is not just formal bookkeeping. In small two-layer networks, conserved quantities correlate strongly with both how fast training converges and how sharp the resulting minimum is, which is why the choice of initialization can be tuned for training efficiency and generalization [§sec_5_2].

Under imbalanced initializations, the imbalance quantity appears explicitly as a term inside convergence-rate bounds, so its magnitude directly sets how fast the bound predicts convergence to be [§sec_5_2].

Training dynamics also tend to erase imbalance on their own. Homogeneous and leaky ReLU networks become automatically balanced during training, matrix factorization under large learning rates shows an implicit regularization bound on the gap between weight-matrix norms, and imbalance is observed to decay exponentially at large learning rates [§sec_5_2].

For losses with a rescaling symmetry, the stationary distribution of SGD is proven to be biased toward balanced solutions, a result later generalized to a mirror-reflection framework covering rescaling, rotation, and permutation symmetries together [§sec_5_2].

Two of the conserved quantity's practical uses are diagnostic rather than theoretical. If a quantity that should stay fixed starts drifting during training, that drift flags either a learning rate too large for the discretization to track the true flow, or a genuine departure from the gradient-flow regime [S1].

Because the quantity's value depends on how weight scale is split across layers before a normalization layer, practitioners can choose an initialization or reparameterization that steers it toward a better-conditioned or flatter minimum before training starts [S1].

## The Math {#the-math}

The invariance argument is a persistence statement about sets, not an inequality: let $P$ be any property expressible purely through the values of conserved quantities. If $P$ holds at the initial parameters, it holds at every later time along the flow, since the quantities on which $P$ depends never change value [§sec_5_2].

The boundary case that makes this concrete is zero imbalance. Initializing with imbalance exactly zero means the invariant's value is zero everywhere along the trajectory, not merely small — this is the strongest of the three convergence-proof conditions in Mechanics, and the one on which the Riemannian gradient-flow result depends [§sec_5_2].

That boundary case also explains why the convergence-rate bounds behave the way they do. Since imbalance appears as a term inside the bound, an initialization with zero imbalance removes that term entirely and gives the tightest guarantee, while nonzero imbalance leaves a residual term that slows the guaranteed rate — which is exactly why large learning rates that drive imbalance toward zero act as an implicit regularizer even before that residual term is analyzed [§sec_5_2].

The level-set picture from Intuition gives the geometric reason this works. Two initializations with different conserved-quantity values sit on two different fixed-dimensional slices of parameter space, and gradient flow cannot cross between slices — so the flat-versus-sharp outcome observed empirically in two-layer networks is not a training accident but a consequence of which slice the initialization landed on [S1].

## Go Deeper {#go-deeper}

- [Symmetries, Flat Minima, and the Conserved Quantities of Gradient Flow](https://arxiv.org/abs/2210.17216) — derives the conserved quantities directly from architectural symmetries and connects them to flat minima, parameterization choices, and training diagnostics; the natural next stop for the formal argument behind this page.
- [Why Momentum Really Works](https://distill.pub/2017/momentum/) — interactive visualizations of gradient-descent trajectories on curved loss surfaces, useful for building intuition for how an invariant constrains a training path before working through the conserved-quantity machinery above.
