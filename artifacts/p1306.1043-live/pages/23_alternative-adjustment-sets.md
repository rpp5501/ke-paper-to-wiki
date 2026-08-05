# Alternative Adjustment Sets
## TL;DR {#tldr}
SID needs an adjustment set to compute each intervention distribution, and the parent set is only one choice among several valid ones. Swapping in a different, principled way to pick that set — most notably the *minimal* adjustment set — changes how the distance is computed but, empirically, barely changes the number you get out. This matters because it tells you SID's verdict on a graph pair is not an artifact of picking parents specifically; the measure is robust to this design choice.

## Intuition {#intuition}
Adjustment sets exist to block confounding paths so that a conditional distribution can stand in for a causal, interventional one — parents are the natural first guess because they sit right next to the intervened node and are trivial to read off the graph. But nothing about the underlying causal logic requires using parents specifically; any set that blocks the right paths works, and some of those sets are smaller, which matters if you care about how much you have to condition on. The question this concept answers is practical rather than theoretical: if you use a *harder-to-compute* but *smaller* adjustment set instead of the free, local parent set, does the resulting notion of graph distance actually change? If it doesn't much, the convenience of parent sets is justified rather than a compromise.

## Mechanics {#mechanics}
**Why parent sets are the default:** they are easy to compute and depend only on the neighbourhood of the intervened node — no need to inspect the rest of the graph — which is exactly why they are widely used in practice for adjustment [§sec_2_4_5].

**What the alternative buys you:** a minimal-size adjustment set keeps the conditioning set as small as possible, which is desirable because smaller conditioning sets generally mean less estimation variance and fewer variables to control for in practice; recent algorithmic advances make this efficiently computable [§sec_2_4_5]. The cost is that minimality is a global property — unlike the parent set, it depends on the whole graph, not just the immediate neighbourhood of the intervened node, so computing it is structurally harder [§sec_2_4_5].

**Non-uniqueness and how it was resolved experimentally:** a minimal adjustment set need not be unique, since several distinct subsets of the same smallest size can all block the relevant paths. The experimental comparison sidesteps this ambiguity by always taking the smallest set the search algorithm happens to find first, rather than trying to characterize or average over all minimal sets [§sec_2_4_5].

**The empirical test:** using the same dense random-graph experimental setup used elsewhere in the paper, SID was computed twice per graph pair — once with parent adjustment, once with the minimal adjustment set — and the two values were compared directly [§sec_2_4_5].

## The Math {#the-math}
No new SID formula is introduced here — the object being varied is the *adjustment-set-selection rule* fed into the same SID computation, not the metric itself. The comparison is therefore best read as a robustness check on a hidden design parameter of SID.

| Property | Parent set | Minimal adjustment set |
|---|---|---|
| Computability | Easy — read directly from the graph | Harder — recent efficient algorithms exist [§sec_2_4_5] |
| Scope of dependence | Local: only the intervened node's neighbourhood [§sec_2_4_5] | Global: depends on the whole graph [§sec_2_4_5] |
| Uniqueness | Unique by definition | Not unique; smallest-found set used in experiments [§sec_2_4_5] |
| Effect on SID (empirical) | Baseline | Differs from baseline only "in about [X]% of the cases" are they exactly equal, and even then differences are small [§sec_2_4_5] |

**Why the near-agreement is the real result:** the paper frames the comparison against a second baseline — the gap between SID and SHD — and reports that the parent-vs-minimal-adjustment gap is small *especially relative to that SID-vs-SHD gap* [§sec_2_4_5]. That relative framing is the load-bearing claim: it is not that the two SID variants are identical, but that whatever discrepancy remains is dominated by the much larger discrepancy SID is designed to fix relative to SHD in the first place. In other words, the choice of adjustment-set rule is a second-order effect on SID, while the choice of *distance itself* (SID vs. SHD) is first-order [§sec_2_4_5].

## Go Deeper {#go-deeper}
- **Motivation and Definition of SID** — the parent-based definition of SID that this concept stress-tests; read it first to see exactly where the adjustment set enters the computation.
- **The dense-random-graph experimental setup** referenced here (used elsewhere to generate the SID-vs-SHD comparisons) — worth revisiting to see the same graphs reused for this robustness check, which is what makes the two comparisons commensurable [§sec_2_4_5].
- **The paper's SID-vs-SHD comparison** — the yardstick this section measures itself against; the "especially compared to" framing only makes sense once that larger gap is in view [§sec_2_4_5].
