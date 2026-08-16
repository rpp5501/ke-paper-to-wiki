# Parameter Symmetry as Data Symmetry in Weight Space Learning

## TL;DR {#tldr}

- When network weights become training data, the permutation symmetry of the input network becomes the data symmetry the processing network must respect [§sec_6_2].
- Architectures for weight-space tasks are built invariant or equivariant to this permutation group, rather than treating weights as an unstructured feature vector [S3][S4].

## Intuition {#intuition}

Think of a hidden layer's neurons as interchangeable: relabeling neuron 3 as neuron 7 (and swapping the corresponding weight rows/columns) produces a numerically different weight vector that computes the exact same function [S1].

A network that predicts something about that weight vector — its accuracy, its architecture family, a generated variant — sees "different" inputs for functionally identical networks unless it is built to ignore, or systematically transform under, that relabeling [§sec_6_2].

## Mechanics {#mechanics}

Designing architectures that process neural network parameters as data has drawn increasing attention, driven by implicit neural representations, weight alignment for model merging, and analysis of the growing number of publicly released trained models [§sec_6_2].

```figure
id: fig_8
caption: The same permutation-relabeling choice splits metanetworks into two families — invariant, when the target (accuracy, INR class) can't depend on relabeling, and equivariant, when the output is itself a set of weights [§sec_6_2]
```

**Invariance versus equivariance is a task-driven choice, not an architectural default.** An invariant metanetwork collapses all permutation-equivalent copies of a network to one output, which is exactly right when the target label — accuracy, INR class — doesn't change under relabeling [fig_8].

An equivariant metanetwork instead transforms its output the same way its input was permuted, which is required when the output is itself a set of weights, as in learning-to-optimize or INR style editing [fig_8].

| Approach | Matches symmetry via | Best suited when | Anchor |
|---|---|---|---|
| Equivariant layer (NFN, DWSNet) | Weight-sharing constrained to commute with the neuron permutation group | Output shape mirrors input weight shape, or must ignore relabeling entirely | [S3][S4] |
| Graph-based metanetwork | Treats the network as a computational graph, inheriting invariance from graph isomorphism | Input networks span different architectures, not one fixed shape | [§sec_6_2] |
| Data augmentation | Generates functionally-equivalent parameter copies via symmetry transforms as extra training examples | An architectural change isn't feasible, or non-permutation symmetries (scaling, sinusoidal) also matter | [§sec_6_2] |

**What each approach actually costs:** an equivariant layer must commute with every permutation in the neuron group, which constrains its weight-sharing pattern far more than an ordinary dense layer and shrinks the learnable function space per parameter [S3][S4].

Data augmentation avoids that architectural constraint by instead multiplying the training set with symmetry transforms of each example, but pays for that freedom in optimization steps: the network must learn the invariance empirically rather than have it hard-wired [§sec_6_2].

**Graph-based metanetworks sidestep the fixed-architecture limit** that early equivariant layers share: by treating the input network as a computational graph and applying a graph neural network, they inherit permutation invariance from graph isomorphism and can learn from diverse architectures rather than one fixed layer-width pattern [§sec_6_2].

**The condition that decides which approach wins:** when the downstream task needs a single fixed output per network — a scalar prediction, a class label — an invariant layer bakes in the guarantee exactly and needs no extra training signal [S3][S4].

When the task instead needs a per-parameter output that must track the input's own permutation, or when the input networks span different architectures, augmentation or graph-based processing wins because they don't require a matching fixed-width equivariant layer [§sec_6_2].

## The Math {#the-math}

**A concrete instance of the symmetry the field is designing around:** take a 2-input, 2-hidden-unit, 1-output network with $W_1=\begin{pmatrix}1&2\\3&4\end{pmatrix}$, $b_1=(0.5,-0.5)$, $W_2=(1,-1)$, input $x=(1,1)$, and ReLU activation [S1].

The forward pass gives hidden pre-activations $h_1=1\cdot1+2\cdot1+0.5=3.5$ and $h_2=3\cdot1+4\cdot1-0.5=6.5$; both stay positive under ReLU, so the output is $1\cdot3.5+(-1)\cdot6.5=-3.0$ [S1].

Now swap hidden units 1 and 2: $W_1'=\begin{pmatrix}3&4\\1&2\end{pmatrix}$, $b_1'=(-0.5,0.5)$, $W_2'=(-1,1)$ — every row and column has moved [S1].

Recomputing gives $h_1'=3+4-0.5=6.5$, $h_2'=1+2+0.5=3.5$, and output $-1\cdot6.5+1\cdot3.5=-3.0$: identical to before, even though all eight weight entries changed [S1].

**This is the redundancy a metanetwork must not be fooled by:** the two parameter vectors are eight different real numbers apiece, so a metanetwork reading them as a flat feature vector sees two unrelated points that encode the identical function [S1][S2].

An invariant layer fixes this by pooling over the neuron dimension before the final layer — summing or max-pooling the hidden units' incoming and outgoing weight rows so the pooled representation matches for $(W_1,b_1,W_2)$ and $(W_1',b_1',W_2')$, guaranteeing $f(g\cdot x)=f(x)$ for every permutation $g$ [S3][S4][fig_8].

An equivariant layer instead uses shared scalar weights per channel — one for a unit's own entry, one for the sum over the rest of the layer — so permuting the input hidden units by $g$ permutes the output by the same $g$, matching how the true weights transform under relabeling [S3][S4][fig_8].

For $k$ hidden units this permutation group has $k!$ elements, so aligning two networks by brute-force search over relabelings does not scale — the motivation for building equivariance in by construction rather than searching for it per pair, which is also the alignment problem Git Re-Basin solves directly [S1][S3][S4].

## Go Deeper {#go-deeper}

- [Git Re-Basin: Merging Models modulo Permutation Symmetries (Paper Explained)](https://www.youtube.com/watch?v=xtaom__-drE) — walks through why permutation symmetry makes independently trained nets' weight spaces non-comparable, with landscape visuals; start here if the redundancy argument above feels abstract.
- [Git Re-Basin: Merging Models modulo Permutation Symmetries](https://arxiv.org/abs/2209.04836) — formalizes the neuron permutation symmetry group used throughout this page and shows how aligning it removes weight-space redundancy.
- [samuela/git-re-basin](https://github.com/samuela/git-re-basin) — README shows the loss-landscape figures directly and the permutation-finding code, making the alignment problem concrete.
- [Equivariant Architectures for Learning in Deep Weight Spaces](https://arxiv.org/abs/2301.12780) — directly addresses how to design layers for weights-as-data that respect permutation symmetry, the mechanism behind the invariant/equivariant layer constructions above.
