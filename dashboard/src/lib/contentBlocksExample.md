```algorithm
title: Algorithm 2 — reachability by repeated squaring
lines:
  - code: "R = A.copy()"
    intent: "Start from one-step reachability: the adjacency matrix itself [§sec_3]"
  - code: "for _ in range(ceil(log2(n))):"
    intent: "Each squaring doubles the path length covered, so ceil(log2 n) rounds reach every simple path in an n-node DAG [§sec_3]"
  - code: "    R = R | (R @ R)"
    intent: "Union keeps paths already found; squaring adds the ones twice as long [§sec_3]"
```

```derivation
shape: Rewrite the intervention distribution over the parent set.
steps:
  - latex: "p(y \\mid do(X = x))"
    why: "The quantity SID compares, written as an intervention rather than a conditioning [eq_1]"
  - latex: "\\sum_{pa(X)} p(y \\mid x, pa(X))\\, p(pa(X))"
    why: "Adjusting for the parents blocks every back-door path, so the sum is computable from observational data [eq_1]"
```

```annotated-eq
latex: "\\mathrm{SID}(G, H) = \\#\\{(i,j) : i \\neq j\\}"
terms:
  - tex: "\\mathrm{SID}"
    role: 1
    words: "The pre-metric being defined — not symmetric, so argument order matters [§sec_3]"
  - tex: "G"
    role: 2
    words: "The true DAG, supplying the intervention distributions treated as correct [§sec_3]"
  - tex: "H"
    role: 3
    words: "The estimated graph, whose parent sets are used as adjustment sets [§sec_3]"
```
