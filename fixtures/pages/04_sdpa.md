# Scaled Dot-Product Attention

## TL;DR {#tldr}

Scaled dot-product attention compares each query Q with keys K, scales the scores, and uses them to mix values V.

## Intuition {#intuition}

Think of softmax as a relevance dial: similar keys receive more of the available attention.

## Mechanics {#mechanics}

Compute query-key scores, divide by the key dimension scale, apply softmax, and multiply by V.

## The Math {#the-math}

$$\operatorname{Attention}(Q,K,V)=\operatorname{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

The factor \(\sqrt{d_k}\) keeps large dot products from saturating softmax.

## Go Deeper {#go-deeper}

Equation eq_1 anchors the scaling operation to the graph nodes that explain it.
