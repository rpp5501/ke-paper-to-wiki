# F(x) := H(x) - x
## TL;DR {#tldr}
- Instead of asking stacked layers to learn a desired mapping H(x) directly, residual learning has them learn the residual F(x) := H(x) - x.
- The block's actual output is reconstructed as F(x) + x, adding the residual back to the input.
- This reformulation targets the degradation problem, where deeper plain networks train worse than shallower ones despite having strictly more representational capacity.

## Intuition {#intuition}
Think of the stacked layers as being asked to describe a change rather than a destination. If the best thing a block can do is nothing at all — pass its input through unchanged — asking it to output "zero" is a much easier target than asking it to reconstruct its own input exactly using nonlinear layers.

Deep plain networks struggle with this reconstruction task. Adding layers should never hurt training error, since extra layers could just learn the identity mapping and leave earlier layers' work untouched — but in practice, solvers have trouble discovering that identity mapping through stacks of nonlinear transformations.

Residual learning sidesteps the difficulty by changing what the layers are asked to compute. Learning "how much to change" from a running total is easier for optimization than learning "what the destination is" from scratch, especially when the answer is close to no change at all.

## Mechanics {#mechanics}
Let H(x) denote the underlying mapping a stack of layers is meant to fit, with x the input to that stack. If nonlinear layers can asymptotically approximate arbitrarily complex functions, they can equally well approximate the residual function H(x) - x, since one hypothesis implies the other [§sec_3_1].

The reformulation sets F(x) := H(x) - x as the function the stacked layers actually learn, so the block's output becomes F(x) + x rather than H(x) directly [§sec_3_1]. Both forms are equally expressive under the approximation hypothesis, but the paper argues they differ in how easy they are to optimize [§sec_3_1].

This design targets the degradation problem directly: if identity mappings are optimal for some added layers, the residual formulation lets the solver drive those layers' weights toward zero rather than forcing it to reconstruct an identity map through nonlinear transformations [§sec_3_1].

In practice, exact identity mappings are unlikely to be optimal, but the paper argues the reformulation still helps by preconditioning the problem [§sec_3_1].

If the optimal underlying function is closer to an identity mapping than to a zero mapping, it should be easier for the solver to find small perturbations referenced to the identity than to relearn the function unreferenced from scratch [§sec_3_1].

The paper reports that learned residual functions tend to have small responses in practice, which it takes as evidence that identity mappings provide reasonable preconditioning [§sec_3_1].

## The Math {#the-math}
```annotated-eq
latex: "F(x) := H(x) - x"
terms:
  - tex: "H(x)"
    role: 1
    words: "The mapping a stack of layers would need to represent directly, under the original non-residual formulation [§sec_3_1]"
  - tex: "x"
    role: 2
    words: "The input to the stack, carried forward as the reference point the residual is measured against [§sec_3_1]"
  - tex: "F(x)"
    role: 3
    words: "The residual the stacked nonlinear layers actually learn; the block's output is reconstructed as F(x) + x [§sec_3_1]"
```

**Boundary case — identity is exactly optimal:** if H(x) = x is the best mapping the block could compute, the residual target becomes F(x) = 0 [§sec_3_1].

Driving every weight in the block toward zero reproduces this exactly, since a stack of linear and nonlinear layers with zero weights outputs zero, and F(x) + x then collapses to x [§sec_3_1].

**More realistic case — identity is close to optimal:** the paper argues exact identity mappings are unlikely to be the true optimum, but the reformulation still preconditions the problem when the optimum is close to one [§sec_3_1].

If H(x) equals x plus some small perturbation δ(x), the residual layers only need to learn F(x) = δ(x), a small function near zero, rather than reconstructing x itself through nonlinear transformations [§sec_3_1].

In the general case where H(x) bears little resemblance to x, the residual formulation offers no particular advantage: F(x) = H(x) - x is just as hard to fit as H(x) itself, since subtracting x is a fixed, learnable-free shift [§sec_3_1].

## Go Deeper {#go-deeper}
- The supplied evidence covers only the residual-learning motivation itself; the mechanism the paper uses to actually implement F(x) + x (shortcut connections, dimension-matching projections) is described elsewhere in the paper and isn't part of the context given here.
- No [eq_N] or [fig_N] evidence was supplied for this concept, so the equation above is drawn from the section's own prose rather than a numbered display equation.
