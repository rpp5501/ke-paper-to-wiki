# Proof: SID for Superset Estimates

## TL;DR {#tldr}

If an estimated DAG H contains every edge of the true DAG G plus nothing else, the parent-based adjustment recipe that defines SID never misfires on G's real edges — those pairs always contribute zero. But the moment H adds even one edge that G does not have, that safety guarantee breaks: the proof exhibits a distribution where the adjustment computed from H's parent sets gives the wrong causal effect, forcing SID(G,H) > 0. Superset estimates are not automatically "free" — SID actively penalizes spurious extra edges, not just missing ones.

## Intuition {#intuition}

Being generous with edges feels safe: if you never deny a real causal relationship, how could you be wrong? The proof says you can still be wrong, because SID doesn't just check whether an edge exists — it uses each node's claimed parent set as a recipe for computing that node's causal effect on everything else. Adding a parent that isn't real changes the recipe. Even though nothing true was removed, the extra ingredient can make the computed effect come out different from the real one, and SID counts that as a miss.

## Mechanics {#mechanics}

The proof splits into two halves matching the two ways a pair (i, j) can be affected by H being a superset of G. The first half handles edges (i, j) that genuinely belong to G, showing the SID contribution there is always zero regardless of what extra edges H carries. The second half handles the case where H invents an edge G doesn't have, and shows this can force a nonzero contribution instead [§sec_9].

**Case 1 — true edges never break.** For (i, j) ∈ G, the argument checks the two-part validity criterion for using pa_H(i) as an adjustment set for the effect of i on j in G. The first part — that every node reachable by a directed path in G is still reachable by a directed path in H — holds automatically because H only ever adds edges to G, never removes them, so no directed path present in G can vanish in H [§sec_9].

The second part needs that any non-directed path blocked by pa_H(i) in H stays blocked in G. Since H is a superset, every path that exists in H's edge set already existed in G's — H cannot introduce a path between two nodes that G lacked, it can only add edges elsewhere. So a path blocked by pa_H(i) in the larger graph H remains a path in the smaller graph G, and blocking is preserved when you go from a bigger graph to a smaller one: a collider that stays unconditioned still blocks, and a conditioned non-collider still blocks, in either graph [§sec_9].

```algorithm
title: Why every true edge of G is safe under a superset estimate H
lines:
  - code: "for each edge (i, j) in G:"
    intent: "SID checks pa_H(i) as the adjustment set for i's effect on j, for every ordered pair [§sec_9]"
  - code: "    check descendants: de_G(i) subset of de_H(i)"
    intent: "H only adds edges, so no directed path present in G can disappear in H [§sec_9]"
  - code: "    check blocking: paths blocked by pa_H(i) in H stay blocked in G"
    intent: "Every path in H already existed in G, and blocking survives when you drop down to a smaller graph [§sec_9]"
  - code: "    conclude: pa_H(i) is a valid adjustment set in G"
    intent: "Both parts of the validity criterion hold, so this pair contributes zero to SID [§sec_9]"
```

**Case 2 — one spurious edge is enough to break it.** Now suppose H contains an edge (i, j) that is not in G. The proof constructs an explicit observational distribution, built from structural equations consistent with G, such that intervening on i produces no change in j's distribution under the true graph — but the adjustment computed from pa_H(i) predicts that it does. The two answers disagree, so this pair is counted wrong and SID(G,H) is strictly positive [§sec_9].

## The Math {#the-math}

The construction fixes structural assignments for every node consistent with G, then compares two quantities for the pair (i, j) where H has the spurious edge: the true interventional quantity computed from G, and the adjustment-based estimate computed by conditioning on pa_H(i). The proof states these two disagree for some value, which is exactly what SID flags as an error at that pair [§sec_9].

```derivation
shape: Why a spurious edge (i,j) in H forces SID(G,H) to be nonzero.
steps:
  - latex: "(i,j) \\in E(H) \\setminus E(G)"
    why: "H claims a direct causal arrow that G does not contain — the extra edge under test [§sec_9]"
  - latex: "p(Y_j \\mid do(X_i = x))"
    why: "The true interventional distribution, fixed by structural equations built to be Markov with respect to G [§sec_9]"
  - latex: "p(Y_j \\mid X_i = x,\\, \\mathrm{pa}_H(i))"
    why: "The estimate SID actually computes, using H's parent set for i as the adjustment set [§sec_9]"
  - latex: "p(Y_j \\mid do(X_i = x)) \\neq p(Y_j \\mid X_i = x,\\, \\mathrm{pa}_H(i))"
    why: "The constructed distribution makes these differ for some x, so the pair (i,j) is counted as an error and SID(G,H) > 0 [§sec_9]"
```

This is why the two halves of the proof are not symmetric in difficulty. Case 1 is a structural fact about DAGs — supersets can only add reachability and can only shrink the graph you have to block paths in, both of which favor validity. Case 2 needs an actual counterexample distribution, because whether a spurious edge breaks the adjustment depends on the numerical structure of the causal mechanisms, not just the graph topology — some spurious edges might get lucky, but the proof only needs one that doesn't [§sec_9].

The asymmetry has a direct consequence for how SID behaves under graph search: a learning algorithm that errs on the side of adding extra edges is not protected from SID penalties the way it might be under a metric that only counts missing edges. Every true edge stays "free" no matter how many extra edges surround it, but each spurious edge is independently a liability [§sec_9].

## Go Deeper {#go-deeper}

- **Metric Properties of SID** — the parent concept this proof belongs to; situates the superset case alongside SID's other structural guarantees (e.g. the subset/CPDAG cases) as part of characterizing when SID is provably zero or provably positive.
- **Proof of the main adjustment-validity proposition** — supplies the two-part criterion (descendant preservation + path-blocking) that Case 1 of this proof applies directly; read it first if the criterion here feels unmotivated.
