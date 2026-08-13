# Residual Learning

## TL;DR {#tldr}
Instead of learning a full mapping $H(x)$ directly, a residual block learns the leftover piece $F(x) := H(x) - x$ and adds it back to the input: output $= F(x) + x$. When identity is already the best mapping, the solver only has to push $F(x)$ toward zero, not reconstruct identity from scratch.

## Intuition {#intuition}
Think of the stacked layers as being asked to sculpt a statue from a block of marble. Learning $H(x)$ from scratch means carving the whole shape blind. Learning $F(x) = H(x) - x$ means starting from a rough cast of the final shape (the input $x$) and only carving the difference.

This matters because very deep plain networks were observed to get worse training error than shallower ones, not from overfitting but because the extra layers struggled to learn even the identity mapping. Residual learning sidesteps that difficulty: identity becomes the easy default, not a hard target.

## Mechanics {#mechanics}
**The setup:** the paper considers an underlying mapping $H(x)$ to be fit by a few stacked layers, with $x$ the input to the first of these layers [§sec_3_1].

**The reformulation:** if nonlinear layers can asymptotically approximate $H(x)$, they can equally approximate the residual $F(x) := H(x) - x$, since $x$ and $H(x)$ share dimensions — so the layers are set to learn $F(x)$ and the block outputs $F(x) + x$ [§sec_3_1].

**Why this is motivated:** the reformulation targets the degradation problem: adding layers to a suitably deep model was observed to raise training error, even though a deeper model can always match a shallower one by setting extra layers to identity [§sec_3_1].

**What breaks without the shortcut:** the degradation problem suggests solvers struggle to approximate an identity mapping using multiple stacked nonlinear layers — not a capacity limit, but an optimization difficulty [§sec_3_1].

**What the shortcut buys the solver:** with the residual formulation, if identity mappings are optimal, the solver can simply drive the weights of the nonlinear layers toward zero to approach identity, rather than fitting identity through nonlinear layers directly [§sec_3_1].

**The general case:** in practice identity is rarely the exact optimum, but the reformulation still preconditions the problem: if the optimal function sits closer to identity than to zero, it is easier for the solver to find small perturbations around identity than to relearn the function from scratch [§sec_3_1].

Empirically, the paper reports that learned residual functions tend to have small responses in general, which the authors read as evidence that identity mappings do provide a reasonable precondition for the layers to build on [§sec_3_1].

## The Math {#the-math}
The residual reformulation is an algebraic identity, not an approximation: defining $F(x) := H(x) - x$ turns the layer's output into $F(x) + x$, which equals $H(x)$ for any $F$ [§sec_3_1].

```derivation
shape: Rewrite the target mapping as a residual plus a shortcut.
steps:
  - latex: "H(x)"
    why: "The mapping stacked layers are hypothesized to approximate directly [§sec_3_1]"
  - latex: "F(x) := H(x) - x"
    why: "Define the residual as the leftover after subtracting the identity, valid because x and H(x) share dimensions [§sec_3_1]"
  - latex: "H(x) = F(x) + x"
    why: "Rearranging shows the layers now only need to learn F(x); the shortcut adds x back for free [§sec_3_1]"
```

```annotated-eq
latex: "F(x) := H(x) - x"
terms:
  - tex: "H(x)"
    role: 1
    words: "The original mapping the stacked layers were hypothesized to fit directly [§sec_3_1]"
  - tex: "x"
    role: 2
    words: "The identity shortcut, carried around the nonlinear layers unchanged [§sec_3_1]"
  - tex: "F(x)"
    role: 3
    words: "The residual the layers are reformulated to learn instead of H(x) [§sec_3_1]"
```

**Boundary case — identity is optimal:** if $H(x) = x$ is truly the best mapping, the residual target becomes $F(x) = 0$, and the solver only needs to push every weight in the block toward zero [§sec_3_1].

**Why that's easier:** driving weights to zero is a well-behaved target for gradient descent, whereas making a stack of nonlinear layers compute the identity exactly has no such simple fixed point to converge on — the degradation problem is evidence that solvers find the latter hard [§sec_3_1].

## Go Deeper {#go-deeper}
This concept is the foundation for **Identity Mapping by Shortcuts**, which specifies how $F(x) + x$ is implemented as an actual layer connection, and builds on **Residual Representations & Shortcuts** in prior work as a prerequisite.
