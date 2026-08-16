That tool call was unnecessary for this task — disregard it. I'll now produce the corrected page directly.

# Loss-Invariant Parameter Transformations and Symmetry

## TL;DR {#tldr}
A parameter-space symmetry is a bijective transformation $T$ of a network's weights that leaves the loss unchanged for every training example, even when it changes what the hidden units compute. The set of all such transformations forms a group, and permutations of hidden units or positive rescalings of ReLU-adjacent weights are the two running examples.

## Intuition {#intuition}
Imagine relabeling the hidden units of a layer — swapping neuron 3 and neuron 7 everywhere they appear. The network computes something different inside, but if you also swap the corresponding rows and columns of the surrounding weight matrices, every input still produces the same loss. That relabeling is a parameter-space symmetry: it changes the parameters, not the score the loss function assigns them.

This is weaker than most people expect from "symmetry." It doesn't require the function to stay pointwise identical — only that the number the loss function reports stays the same. That gap is where a whole group of transformations lives, and it's the object this page defines precisely.

## Mechanics {#mechanics}
The loss function factors into a network $f$ and a cost $\Cost$: $L(\theta,(x,y)) := \Cost(f(\theta,x), y)$, so $\theta$ ranges over parameters, $x$ over inputs, and $y$ over target labels [§sec_2_1].

A parameter-space symmetry is a bijective map $T\colon\Par\to\Par$ such that $L(\theta) = L(T(\theta))$ for every data point — the transformation may change $\theta$ entirely, as long as the loss it produces does not move [§sec_2_1].

$G_{\Theta,L}$, the set of all such transformations, forms a group under composition, because each of the four group properties follows directly from what loss-invariance requires:

- Closure: composing two loss-preserving maps preserves loss, because the second map's invariance applies to the output of the first [§sec_2_1][S1]
- Associativity: composition of functions is always associative, so this holds for free [§sec_2_1]
- Identity: the identity map leaves $\theta$, and therefore $L(\theta)$, unchanged, so it is always in the set [§sec_2_1]
- Inverse: every $T$ is bijective, so $T^{-1}$ exists and satisfies $L(T^{-1}(\theta)) = L(\theta)$, since $T^{-1}(\theta)$ is itself a valid parameter that $T$ maps back to $\theta$ [§sec_2_1][S1]

Data splits into inputs $\Data_{\text{input}}$ and targets $\Data_{\text{target}}$ because a symmetry can act on both halves jointly [§sec_2_1].

Permuting hidden or output indices in $\theta$ only preserves loss if the labels are read against the permuted outputs consistently, so invariance is checked against the paired $(x,y)$ distribution rather than against $x$ alone [S1][S2].

Loss-invariance is strictly weaker than requiring the network function itself to stay unchanged [S2].

Permuting hidden units changes the values computed at those interior neurons, so $f(\theta, x) \neq f(T(\theta), x)$ pointwise inside the network [S2].

The composed input-to-loss map is still identical for every training pair, because the permutation is undone by the time the output reaches the labels — so $L(\theta) = L(T(\theta))$ holds even though the function's internals differ [S2].

A group action formalizes this: it is a map $G\times\Par\to\Par$ satisfying $e\cdot\theta=\theta$ and $g\cdot(g'\cdot\theta)=(gg')\cdot\theta$, so composing group elements matches composing their transformations [§sec_2_1].

When the action is linear, it factors through a representation $\rho\colon G\to \GL_n(\R)$, a homomorphism satisfying $\rho(g_1g_2)=\rho(g_1)\rho(g_2)$, which lets abstract group elements act on parameter space as concrete invertible matrices [§sec_2_1].

Three subgroups recur throughout this framework: $\GLn(\R)$ (all invertible $n\times n$ matrices), $O_n(\R)$ (matrices whose transpose equals their inverse), and $\R_{>0}^h$ (positive diagonal scalings) — alongside the symmetric group $S_n$, permutations of $n$ indices [§sec_2_1].

```figure
id: fig_1
caption: D3, the symmetry group of a triangle, illustrates the same axioms parameter-space symmetries satisfy — an identity element, associative composition, and an inverse for every transformation [§sec_2_1]
```

## The Math {#the-math}

```annotated-eq
latex: "L(\\theta) = L(T(\\theta))"
terms:
  - tex: "L"
    role: 1
    words: "The scalar loss, the only quantity a parameter-space symmetry is required to preserve [§sec_2_1]"
  - tex: "\\theta"
    role: 2
    words: "The original parameter vector before the transformation is applied [§sec_2_1]"
  - tex: "T(\\theta)"
    role: 3
    words: "The transformed parameters — can differ from $\\theta$ at every coordinate and still satisfy the equation [§sec_2_1]"
```

**A permutation that changes the function but not the loss:** take a network with one input, two hidden ReLU units, and one output, $h=\mathrm{ReLU}(W_1x)$, $\hat y = W_2h$ [§sec_2_1].

- Original weights $W_1=(3,7)^\top$, $W_2=(2,5)$, input $x=1$: hidden activations $h=(3,7)$, output $\hat y = 2(3)+5(7)=41$ [S2]
- Swap the two hidden units: $W_1'=(7,3)^\top$, $W_2'=(5,2)$: hidden activations $h'=(7,3)$, a different vector, so $f$ changes pointwise at the hidden layer [S2]
- Output is unchanged: $\hat y' = 5(7)+2(3)=41=\hat y$, so for every downstream loss $\Cost(\hat y, y)=\Cost(\hat y', y)$, and $T$ is loss-invariant without being the identity [S2]

**Positive rescaling is a second non-identity example:** ReLU is positive-homogeneous, $\mathrm{ReLU}(cz)=c\,\mathrm{ReLU}(z)$ for $c>0$, so scaling a hidden unit's incoming weight by $c$ and its outgoing weight by $1/c$ leaves every output unchanged [S1].

- With $W_1=3$, $c=2$: incoming weight becomes $6$, hidden activation becomes $\mathrm{ReLU}(6\cdot1)=6=2\cdot\mathrm{ReLU}(3\cdot1)$, confirming the homogeneity used above [S1]
- Outgoing weight $W_2=5$ becomes $2.5$: output is $2.5\times6=15$, matching the original $5\times3=15$, so loss is identical for any label $y$ [S1]

What if $c$ is negative? ReLU homogeneity fails for negative $c$ since $\mathrm{ReLU}(cz) \neq c\,\mathrm{ReLU}(z)$ whenever $z>0$, so this transformation only belongs to the symmetry group when $c>0$ — exactly why the relevant subgroup is $\R_{>0}^h$ and not all of $\R^h$ [§sec_2_1][S1].

## Go Deeper {#go-deeper}
- [On the Symmetries of Deep Learning Models and their Internal Representations](https://arxiv.org/abs/2205.14258) — gives the formal definition of loss-invariant parameter transformations and proves they form a group, distinguishing loss-invariance from stricter functional invariance. Start here.
- [Git Re-Basin: Merging Models modulo Permutation Symmetries](https://arxiv.org/abs/2209.04836) — Figure 1 diagrams two permutation-related parameter settings that are loss-invariant, and Section 2 sets up invariance over paired input/label data.
- [git-re-basin (reference implementation)](https://github.com/samuela/git-re-basin) — concrete code showing how a loss-invariant re-parameterization is searched for and applied to real network weights.
