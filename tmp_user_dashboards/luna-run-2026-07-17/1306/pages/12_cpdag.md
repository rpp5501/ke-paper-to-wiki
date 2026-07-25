# Completed Partially Directed Acyclic Graph (CPDAG)

## TL;DR {#tldr}
A graph representing a Markov equivalence class of DAGs with compelled directed edges and reversible undirected edges. The paper evaluates graphs by causal consequences rather than edge edits alone.

## Intuition {#intuition}
A CPDAG keeps arrowheads that every DAG in an equivalence class agrees on and leaves reversible adjacencies undirected.

## Mechanics {#mechanics}
Constraint-based discovery methods may identify a Markov equivalence class rather than a unique DAG. The paper therefore extends SID comparisons to CPDAGs, where multiple DAG completions are possible. [§sec_1]

## The Math {#the-math}
A CPDAG represents a class C of Markov-equivalent DAGs: [§sec_1]

$$C=\{G: G\text{ has the same d-separations as the represented CPDAG}\}. $$ [§sec_1]

## Go Deeper {#go-deeper}
- Read the paper's full-text PDF section for the formal definition, examples, proofs, and implementation details. [§sec_1]
- This page is grounded in the supplied local PDF; no external research note was used. [S1]
