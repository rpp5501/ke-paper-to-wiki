# Parameter Identifiability and Completeness of Symmetry

## TL;DR {#tldr}
- The realization map ρ sends parameters to the function they compute; a *fiber* is the set of all parameter settings that compute the same function [§sec_2_4].
- A symmetry group is *complete* for a fiber when it can reach every point in that fiber from every other point — it acts transitively on the fiber [§sec_2_4].
- RBF networks, tanh networks, and MoE gating are proven complete under permutation (plus sign-flip); ReLU networks are only complete in restricted or generic settings, and can carry *hidden* symmetries the known group misses [§sec_2_4].

## Intuition {#intuition}

Think of a function's fiber as a room, and the known symmetry group — permutations, sign flips, positive rescalings — as a set of doors between parameter settings in that room. Completeness asks whether those doors reach every corner. [§sec_2_4]

If some parameter setting has no known-symmetry door leading to it from another point that computes the identical function, the group is incomplete: a hidden symmetry connects those two points instead. [§sec_2_4]

This matters for interpreting or comparing trained networks: if you compare two networks' weights without knowing the complete symmetry group, you can't tell whether a difference reflects a real functional difference or just an unaccounted reparameterization. [§sec_2_4]

## Mechanics {#mechanics}

The realization map ρ: Par → F sends a parameter θ to the function it computes, ρ(θ). The fiber ρ⁻¹(f) is the set of all parameters computing a given function f — when ρ is not injective, this fiber contains more than one point, so the function alone does not pin down the parameters. [§sec_2_4]

```annotated-eq
latex: "\\rho\\colon \\Par \\to \\mathcal{F}"
terms:
  - tex: "\\rho"
    role: 1
    words: "The realization map — the only object linking a parameter setting to the behavior it produces [§sec_2_4]"
  - tex: "\\Par"
    role: 2
    words: "The parameter space; a single point here is one weight setting, not one function [§sec_2_4]"
  - tex: "\\mathcal{F}"
    role: 3
    words: "The function space; two different points of Par can land on the same point here, which is exactly what a fiber captures [§sec_2_4]"
```

A symmetry group G acting on Par is complete for a fiber if it acts transitively on it — any two parameters in the fiber are related by some g ∈ G. [§sec_2_4]

If G is complete for every fiber of a loss L, the parameters of L are called identifiable up to G, and no symmetry outside G is needed to explain the redundancy. [§sec_2_4]

| Architecture | Known-complete group | Status |
|---|---|---|
| Gaussian RBF networks | Permutation | Proven complete [§sec_2_4] |
| Tanh feedforward networks | Permutation + sign-flip | Proven complete under stated conditions [§sec_2_4] |
| Complex-tanh / tanh RNN / σ(0)=0, σ'(0)≠0, σ''(0)=0 / asymptotically constant activations | Permutation + sign-flip (architecture-dependent) | Proven complete [§sec_2_4] |
| MoE gating | Permutation + translation | Proven complete [§sec_2_4] |
| Two-layer ReLU (non-degenerate) | Permutation + positive scaling | Complete, excluding the identical-zero-hyperplane degeneracy [§sec_2_4] |
| General ReLU networks | Permutation + positive scaling | Complete only on a positive-measure subset; hidden symmetries exist elsewhere [§sec_2_4][S1] |
| Polynomial / monomial networks | Permutation + scaling | Proven complete (monomial case); finitely many extra symmetries for general polynomial activations [§sec_2_4] |
| Lightning self-attention layers | Three named rescaling symmetries | Proven complete; softmax breaks only one of the three [§sec_2_4] |

Grigsby, Lindsey, Masden and Pelella show that even for generic weights, ReLU networks admit hidden symmetries — reparameterizations that preserve the function but lie outside permutation and positive scaling [S1].

Godfrey et al. instead show the classical group is complete once dead neurons and duplicate rows are excluded, using the intertwiner group of the parameter-to-function map [S2].

Functional dimension — the rank of the Jacobian of ρ — offers a concrete test: if a known group's orbit is smaller than this rank requires, a hidden symmetry must exist [S3].

**Positive results for ReLU require extra structure.** [§sec_2_4]
- Excluding the degenerate case where two neurons share an identical zero hyperplane, two-layer ReLU networks have no symmetries beyond permutation and positive scaling [§sec_2_4].
- If parameters within each linear region compute the same linear function, the boundaries between linear regions alone determine parameters up to permutation and positive scaling [§sec_2_4].
- Networks with non-increasing layer widths, or all layers wider than the input, have no hidden symmetries on a positive-measure subset of parameters; this probability rises with input and layer width and falls with depth [§sec_2_4].

For polynomial neural networks, permutation and scaling are conjectured to be the only symmetries; this is proved for the monomial case, with only finitely many extra symmetries for general polynomial activations [§sec_2_4]. Convolutional networks with polynomial activations generically have no nontrivial data-independent symmetries at all [§sec_2_4].

## The Math {#the-math}

Consider the single ReLU neuron realization map ρ: (a,b) ↦ (x ↦ ReLU(ax+b)). Both (0,0) and (0,-1) lie in ρ⁻¹(0), the fiber of the constant-zero function, since ReLU(0·x+0)=0 and ReLU(0·x-1)=0 for every x. [§sec_2_4]

A lone neuron has nothing to permute with. Positive scaling sends (a,b) to (ca,cb) for c>0, so scaling (0,-1) can only reach (0,-c) for c>0 — never (0,0). [§sec_2_4]

The fiber therefore contains two points the known group cannot connect: a witness that its orbits are strictly smaller than the fiber itself, exactly the hidden-symmetry phenomenon described above [§sec_2_4].

Functional dimension is the rank of the Jacobian of ρ at a parameter, measuring how many independent directions locally perturb the realized function [S3].

When a fiber's known-symmetry orbit has lower dimension than this rank requires, some parameter directions leave the function unchanged without being explained by the group — a hidden symmetry is then guaranteed, not merely possible [S3].

## Go Deeper {#go-deeper}

- [Hidden Symmetries of ReLU Networks](https://arxiv.org/abs/2306.06179) — the source of the (0,0)/(0,-1) counterexample above; the right place to see more hidden-symmetry constructions worked out.
- [On the Symmetries of Deep Learning Models and their Internal Representations](https://arxiv.org/abs/2205.14258) — defines the intertwiner group formally and proves permutation-plus-scaling suffices for generic (non-degenerate) ReLU networks.
- [Functional Dimension of Feedforward ReLU Neural Networks](https://arxiv.org/abs/2209.04036) — the dimension-counting machinery behind the functional-dimension argument used in The Math.
