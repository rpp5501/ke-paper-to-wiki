# Causal DAG

## TL;DR {#tldr}
A directed acyclic graph whose arrows encode the causal structure used to derive intervention distributions. The paper evaluates graphs by causal consequences rather than edge edits alone.

## Intuition {#intuition}
A causal DAG is a wiring diagram with no directed loops. Its arrows are not merely correlations: they state which variables may directly transmit changes to which others.

## Mechanics {#mechanics}
The paper uses a finite variable family X and a DAG G to connect graph structure to Markov distributions and intervention statements. Parents, descendants, paths, and d-separation are the vocabulary used by every SID criterion. [§sec_1]

## The Math {#the-math}
A DAG has directed edges and no directed cycle; the parent set of node j is written pa_G(j). [§sec_1]

$$G\text{ is a DAG}\;\Longrightarrow\;\text{its directed paths define ancestors and descendants without cycles}. $$ [§sec_1]

## Go Deeper {#go-deeper}
- Read the paper's full-text PDF section for the formal definition, examples, proofs, and implementation details. [§sec_1]
- This page is grounded in the supplied local PDF; no external research note was used. [S1]
