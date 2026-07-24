# Structural Intervention Distance (SID)

## TL;DR {#tldr}
A graph-based pre-distance that counts ordered intervention questions whose causal distributions are falsely predicted by an estimated graph relative to a true graph. The paper evaluates graphs by causal consequences rather than edge edits alone.

## Intuition {#intuition}
Imagine testing every ordered question "if I force variable i, what happens to variable j?" SID is the number of those questions for which an estimated graph gives the wrong causal answer relative to the true graph.

## Mechanics {#mechanics}
The true DAG is G and the estimated DAG is H. For every ordered pair (i,j), the estimate is checked as a causal predictor, so a small edge edit can count many times if it changes downstream intervention logic. The score is directional because H is judged against G. [§sec_1]

## The Math {#the-math}
The paper defines SID as the number of ordered pairs with a falsely estimated intervention distribution. [§sec_1]

$$\operatorname{SID}(G,H)=\#\{(i,j): i\ne j,\;H\text{ falsely predicts the intervention distribution from }i\text{ to }j\}. $$ [§sec_1]

## Go Deeper {#go-deeper}
- Read the paper's full-text PDF section for the formal definition, examples, proofs, and implementation details. [§sec_1]
- This page is grounded in the supplied local PDF; no external research note was used. [S1]
