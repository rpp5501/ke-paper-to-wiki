# Retraction and Count-Spiking Examples

## TL;DR {#tldr}
Four hand-picked completions show the same shape: the model backtracks with a phrase like "Wait — that's a contradiction," and at that exact token the Remaining-Count Probe's prediction $\hat{r}_t$ jumps upward even though the true remaining length $r_t$ keeps counting down normally.

The four retraction phrases sit at different positions and use different wording, so the spike is not an artifact of one specific trigger string — but with only four examples, drawn deliberately from the worst-predicted completions, this is a qualitative pattern, not a measured rate.

## Intuition {#intuition}
Picture a student working through a long proof who suddenly says, "wait, that's wrong." At that moment their sense of how much work remains should jump — they know they have to backtrack, reconsider, and rewrite before reaching the end again.

The probe shows exactly that reflex: at the retraction token, $\hat{r}_t$ jumps to a value far larger than the position actually has left, because the surface pattern of a backtrack resembles the surface pattern of a completion with much more still to write. The true count keeps ticking down through the same token.

## Mechanics {#mechanics}
These four completions are not a random sample: the eval set was sorted by per-completion MAE and walked down from the worst, so all four come from the region where the probe's predictions are farthest from the ground truth [§sec_8_9].

That selection choice licenses only a directional claim. It confirms the same jump-then-recover shape recurs across independent completions, but says nothing about how often the shape appears in the eval set as a whole [§sec_8_9].

Each panel comes from a token-by-token explorer that logs, at every position $t$, the token itself, the ground-truth remaining count $r_t$, and the probe's prediction $\hat{r}_t$, shown as both a table column and a bar height [§sec_8_9].

| Example | Position | Trigger phrase | Peak $\hat{r}_t$ | Local baseline $\hat{r}_t$ |
|---|---|---|---|---|
| 1 | ~469 | "Wait — that's a contradiction" | ≈353 | not reported [fig_6] |
| 2 | 608 | "Wait — but that would mean …" | ≈369 | ≈130–170 [fig_7] |
| 3 | 261 | "But let's check the exact wording" | ≈366 | ≈220–280 [fig_8] |
| 4 | ~500 (row 494) | "But let's look again … Wait — perhaps the phrase …" | ≈341 (first of two spikes) | not reported [fig_9] |

```figure
id: fig_6
caption: The retraction phrase "Wait — that's a contradiction" at position 469 sends $\hat{r}_t$ to about 353 while $r_t$ keeps counting down normally [§sec_8_9]
```

```figure
id: fig_7
caption: At position 608, right after the candidate answer "20 flashlights," the word "Wait" alone lifts $\hat{r}_t$ from a 130–170 baseline to about 369 [§sec_8_9]
```

```figure
id: fig_8
caption: At position 261, "But let's check the exact wording" pulls $\hat{r}_t$ from a 220–280 baseline up to a local peak of about 366 [§sec_8_9]
```

```figure
id: fig_9
caption: A doubled retraction near position 500 — "But let's look again" followed by "Wait — perhaps the phrase" — produces two elevated clusters, the first peaking at about 341 [§sec_8_9]
```

The four trigger phrases differ in wording and land at different positions, yet each produces the same shape: a sharp upward jump in $\hat{r}_t$ at the retraction token. That recurrence is what licenses the claim that the spike is not tied to one specific trigger string [§sec_8_9].

## The Math {#the-math}
Two of the four panels report an explicit local baseline, which is enough to size the spike as a ratio. In example 2, $\hat{r}_t$ rises from a baseline of about 130–170 to 369 at the "Wait" token — roughly 2.2×–2.8× the surrounding prediction, an excess of about 200–240 tokens [fig_7].

Example 3 spikes from a baseline of about 220–280 to a peak of 366 — a smaller relative jump, roughly 1.3×–1.7×, or an excess of 86–146 tokens. The same absolute mechanism produces a larger ratio in example 2 only because its baseline is lower [fig_8].

Examples 1 and 4 report only the peak value, 353 and 341, with no stated local baseline, so no ratio is computable for them from the evidence supplied; the two computable ratios above are the strongest quantitative statement the four panels support [§sec_8_9].

The reason a single retraction token dominates MAE is arithmetic, not modeling: if the true remaining count near the retraction is on the order of tens to low hundreds, a prediction 130–240 tokens too high contributes an absolute error of that same size from one token alone, comparable to the error the model would otherwise accumulate over many tokens combined [§sec_8_9].

That single-token cost is why the panels were found by sorting on MAE in the first place: a completion containing one retraction spike this large will rank among the worst regardless of how accurate the probe is everywhere else in that completion [§sec_8_9].

A four-example gallery cannot support a claim about how often retraction spikes occur. The paper is explicit that this is future work: a systematic version would pair retraction-token shifts against a length-matched non-retraction control population and report the aggregate distribution of upward shifts in $\hat{r}_t$ [§sec_8_9].

Without that control population, there is no denominator — no count of retraction tokens where the probe did not spike, and no baseline rate for spikes on non-retraction tokens to compare against. Four hand-picked worst-case examples cannot supply either number [§sec_8_9].

## Go Deeper {#go-deeper}
No external resources were supplied for this concept. The single curated retraction example referenced in the parent concept, Dynamic Re-Estimation and Spiking, is the primary walkthrough of the phenomenon; the four panels here are the paper's additional qualitative support for that same pattern, drawn from the same high-loss selection procedure.
