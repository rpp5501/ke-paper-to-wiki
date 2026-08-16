# Symmetries in Transformers

## TL;DR {#tldr}

- Each attention head carries a continuous $\text{GL}_{d_k}(\R)$ symmetry (and, in multi-head attention, a $\text{GL}_{d_v}(\R)$ symmetry) from reparametrizing its QK and OV circuits.
- Multi-head attention adds a discrete $S_h$ symmetry: permuting heads and the matching rows of the output projection leaves the layer unchanged.
- LoRA adapters carry their own $\text{GL}_r(\R)$ symmetry; LayerNorm contributes an independent positive-scale symmetry.
- These compose layer by layer, so a transformer's full symmetry group grows combinatorially with heads and depth rather than forming one simple group.

## Intuition {#intuition}

Each attention head only ever uses its weights through the products $W^Q(W^K)^T$ and $VW^V$, never the factors on their own. Slipping an invertible matrix and its inverse between the two factors of a product is invisible to anything downstream — the same trick that lets you insert a matrix and its inverse anywhere in a chain of matrix multiplications.

Heads themselves are like interchangeable workers on parallel assembly lines: once their outputs are concatenated and mixed by a shared projection, relabeling which worker is "head 1" changes nothing about the total. LayerNorm's symmetry is a units trick — since it divides out the scale of its input, feeding it weights measured in different units produces the same normalized output.

## Mechanics {#mechanics}

**Single-head attention.** The self-attention function maps query, key, and value weights $(W^Q, W^K, W^V) \in \R^{d_m \times d_k} \times \R^{d_m \times d_k} \times \R^{d_m \times d_v}$ to an output built from $QW^Q(KW^K)^T$ and $VW^V$ [eq_3].

Because the score depends only on the product $W^Q(W^K)^T$, absorbing $g \in \text{GL}_{d_k}(\R)$ and $g^{-1}$ between the two factors leaves the softmax unchanged: $g \cdot (W^Q, W^K, W^V) = (W^Q g^{-1}, W^K g^T, W^V)$ [S1].

**Multi-head attention.** Multi-head attention concatenates $h$ head outputs and applies a shared output projection, $\text{MultiHead}(Q,K,V) = \text{Concat}(\text{head}_1,...,\text{head}_h)W^O$, with $\text{head}_i = \text{Attention}(QW_i^Q, KW_i^K, VW_i^V)$ [§sec_2_2_2].

Each head inherits its own $\text{GL}_{d_k}(\R)$ symmetry, so before any cross-head structure is added, the $h$ heads together already carry a $(\text{GL}_{d_k}(\R))^h$ symmetry [§sec_2_2_2].

```figure
id: fig_3
caption: Where each transformer symmetry lives — GL(d) inside a single head's QK/OV circuit versus S_h across concatenated heads [§sec_2_2_2]
```

**Head permutation.** Heads interact only through concatenation and the shared output projection $W^O$, never directly with each other, so which head is labeled "head 1" versus "head 2" leaves no trace in the function computed [§sec_2_2_2].

Consistently permuting the heads and the matching rows of $W^O$ therefore leaves the layer's output unchanged: $\pi \cdot (W_i^Q, W_i^K, W_i^V, W_i^O) = (W_{\pi^{-1}(i)}^Q, W_{\pi^{-1}(i)}^K, W_{\pi^{-1}(i)}^V, W^O_{\pi^{-1}(i)})$ for $\pi \in S_h$ [§sec_2_2_2].

This is the same discrete symmetry found generally in networks with interchangeable hidden units, applied here at the granularity of whole heads rather than individual neurons [S2].

**Per-head output symmetry.** Each head also carries a $\text{GL}_{d_v}(\R)$ symmetry: rescaling its value weights by $g_i^{-1}$ and the matching rows of $W^O$ by $g_i$ cancels before reaching the residual stream, $g_i \cdot (W_i^Q, W_i^K, W_i^V, W_i^O) = (W_i^Q, W_i^K, W_i^V g_i^{-1}, g_i W^O_i)$ [§sec_2_2_2].

**LoRA.** Low-rank adaptation writes an update as $W + UV$ with $U \in \R^{n \times r}$, $V \in \R^{r \times m}$; inserting $g \in \text{GL}_r(\R)$ and $g^{-1}$ between them, $g \cdot (U, V) = (Ug^{-1}, gV)$, leaves $UV$ unchanged [§sec_2_2_2].

**LayerNorm scale symmetry.** LayerNorm normalizes its input, so rescaling the weights feeding into it by any positive constant leaves the normalized activations unchanged, adding a continuous scale symmetry independent of the attention symmetries above [S3].

**Composition across depth.** The per-head $\text{GL}_{d_k}(\R)$ and $\text{GL}_{d_v}(\R)$ symmetries, the per-layer $S_h$ permutation, and each LayerNorm's scale symmetry combine via (semi)direct products layer by layer, so the full network's symmetry group grows combinatorially with heads and depth rather than forming one simple group [S1][S2][S3].

| Component | Symmetry type | Group | What it does |
|---|---|---|---|
| Single-head attention | Continuous | $\text{GL}_{d_k}(\R)$ | Reparametrizes the QK circuit without changing scores [eq_3] |
| Multi-head attention | Discrete | $S_h$ | Permutes which head is which [§sec_2_2_2] |
| Multi-head attention | Continuous | $(\text{GL}_{d_v}(\R))^h$ | Rescales each head's value/output pair [§sec_2_2_2] |
| LoRA | Continuous | $\text{GL}_r(\R)$ | Reparametrizes the low-rank factors $U,V$ [§sec_2_2_2] |
| LayerNorm | Continuous | positive scale | Rescales incoming weights [S3] |

## The Math {#the-math}

$$
\text{Attention}(QW^Q, KW^K, VW^V) = \text{softmax}\left( \frac{QW^Q (KW^K)^T}{\sqrt{d_k}} \right) VW^V
$$
[eq_3]

```annotated-eq
latex: "\\text{Attention}(QW^Q, KW^K, VW^V) = \\text{softmax}\\left( \\frac{QW^Q (KW^K)^T}{\\sqrt{d_k}} \\right) VW^V"
terms:
  - tex: "QW^Q(KW^K)^T"
    role: 1
    words: "The raw attention scores — a product of the two weight matrices rather than either alone, exactly the factorization the GL_{d_k} symmetry exploits [eq_3]"
  - tex: "\\sqrt{d_k}"
    role: 2
    words: "A fixed scalar normalizer that does not touch the weights, so it plays no role in the symmetry [eq_3]"
  - tex: "VW^V"
    role: 3
    words: "The value projection, linear and untouched by the QK-side symmetry, giving it its own independent GL_{d_v} symmetry in the multi-head case [eq_3]"
```

The $\text{GL}_{d_k}(\R)$ invariance is a direct algebraic cancellation, not an approximation:

```derivation
shape: Show that inserting an invertible $g \in \text{GL}_{d_k}(\R)$ into the QK circuit leaves the attention scores unchanged.
steps:
  - latex: "(QW^Qg^{-1})(KW^Kg^{T})^T = QW^Qg^{-1}(g^{T})^T(KW^K)^T"
    why: "Expand the transpose of the product so the inserted matrices sit next to each other [eq_3]"
  - latex: "= QW^Qg^{-1}g(KW^K)^T = QW^Q(KW^K)^T"
    why: "$(g^T)^T = g$, so $g^{-1}g$ cancels to the identity, recovering the original score matrix exactly [eq_3]"
```

A boundary case worth checking: at $d_k = 1$, $\text{GL}_1(\R)$ is just the nonzero reals under multiplication, so the symmetry reduces to scaling $W^Q$ up by any $c \neq 0$ while scaling $W^K$ down by $c$ — the one-dimensional shadow of the cancellation above [eq_3].

## Go Deeper {#go-deeper}

- [A Mathematical Framework for Transformer Circuits](https://transformer-circuits.pub/2021/framework/index.html) — works through the QK/OV circuit algebra directly, showing via matrix diagrams exactly which weight transformations leave a head's function unchanged. Start here.
- [Git Re-Basin: Merging Models modulo Permutation Symmetries](https://arxiv.org/abs/2209.04836) — formalizes the head/hidden-unit permutation symmetry and how it composes layer-by-layer across a whole network.
- [Neural Mechanics: Symmetry and Broken Conservation Laws in Deep Learning Dynamics](https://arxiv.org/abs/2012.04728) — derives the scale symmetry introduced by normalization layers and how it interacts with training dynamics.
