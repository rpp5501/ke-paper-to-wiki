# Loss Symmetry

## TL;DR {#tldr}
A loss symmetry is a group action on the parameter space that leaves the loss $L$ unchanged, even when it changes the network function $f$ itself [§sec_2_3_1]. It is a relaxation of functional symmetry: every functional symmetry is a loss symmetry, but the converse fails [eq_4].

## Intuition {#intuition}
Think of loss symmetry as asking a weaker question about a parameter transformation: does training still see the same objective, not does the network compute the same thing [§sec_2_3_1].

Functional symmetry requires that every group action leave the feedforward function $f$ itself unchanged, and invariance of the loss $L$ follows automatically because $L$ is built from $f$ [§sec_2_3_1].

Loss symmetry drops that requirement on $f$ and asks only that $L$ stay fixed, so the group can act on parameters in ways that visibly change what the network computes [§sec_2_3_1].

This is why loss symmetry sits as a relaxed definition of symmetry rather than a synonym for functional symmetry — the two concepts contrast on precisely this point [§sec_2_3_1].

## Mechanics {#mechanics}
A loss symmetry is defined directly on the loss rather than on the model: it is any action of a group $G$ on the parameter space $\Par$ such that $L(g\cdot\theta,x)=L(\theta,x)$ for every $g\in G$, every $\theta\in\Par$, and every $x\in\Data$ [eq_4].

Because $L$ is typically the composition of a model $f$ with a cost function $\Cost$, a transformation that leaves $f$ fixed automatically leaves $L$ fixed too. This is exactly the definition of functional symmetry, so every functional symmetry is a special case of a loss symmetry [§sec_2_3_1].

The self-supervised linear-network example shows the relaxation doing real work: for $f(W,x)=Wx$ with $W\in\R^{m\times n}$, take a loss that depends on $f$ only through the inner product $f(x)^Tf(x')$ for data pairs $x,x'\in\R^n$ [§sec_2_3_1].

The group $O(m)$ acts on this single layer by $g\cdot W = gW$, and this action preserves $L$ while changing the feedforward function itself, since $Wx$ and $gWx$ are different vectors whenever $g\neq I$ [§sec_2_3_1].

This action is distinct from the layer-wise symmetry of a deep linear network, where a transformation on one layer must be canceled by an inverse transformation on an adjacent layer to leave $f$ unchanged; here there is no adjacent layer to cancel against, so $f$ is genuinely altered [§sec_2_3_1].

## The Math {#the-math}
The formal definition of loss symmetry reproduces the invariance condition on $L$ directly, with no reference to $f$ at all:

$$
L(g \cdot , x) = L(, x),\quad \forall g \in G,\quad \forall  \in \Par,\quad \forall x \in \Data.
$$
[eq_4]

This equation says the group action can move a parameter anywhere in its orbit under $G$ without moving the value $L$ assigns to any data point $x$ — nothing here constrains where the action sends $f$ [eq_4].

The self-supervised linear-network example turns this into an explicit computation, since the assumed loss depends on $f$ only through the inner product $f(x)^Tf(x')$ [§sec_2_3_1]:

```derivation
shape: Show that g·W = gW with g ∈ O(m) leaves the inner product f(x)^Tf(x') fixed even though f itself changes.
steps:
  - latex: "f(gW,x)^Tf(gW,x') = (gWx)^T(gWx')"
    why: "Substitute the group action g·W = gW into f(W,x) = Wx for both data points [§sec_2_3_1]"
  - latex: "(gWx)^T(gWx') = x^TW^Tg^Tg\\,Wx'"
    why: "Expand the transpose of a product, (AB)^T = B^TA^T, term by term [§sec_2_3_1]"
  - latex: "x^TW^Tg^Tg\\,Wx' = x^TW^TWx'"
    why: "g ∈ O(m) means g^Tg = I, the defining property of the orthogonal group, so the two g factors cancel [§sec_2_3_1]"
  - latex: "x^TW^TWx' = f(W,x)^Tf(W,x')"
    why: "The surviving expression is exactly the untransformed inner product, so L — which depends on f only through this quantity — takes the same value before and after the group action [§sec_2_3_1]"
```

This is why the symmetry is a loss symmetry and not a functional one: the last line shows the quantity $L$ actually reads is unchanged, while $f(gW,x) = gWx \neq Wx = f(W,x)$ for $g \neq I$ shows the function itself moved [§sec_2_3_1].

## Go Deeper {#go-deeper}
No resource was supplied for this concept, so there is no external link to add here. The most useful next step is comparative: read Functional Neural Network Symmetry side by side with this page, since loss symmetry is defined by relaxing exactly the requirement that page states, and the self-supervised linear-network example above is the clearest case where the two diverge [§sec_2_3_1].
