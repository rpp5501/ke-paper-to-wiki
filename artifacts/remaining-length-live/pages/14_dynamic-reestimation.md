# Dynamic Re-Estimation and Spiking

## TL;DR {#tldr}
On one curated example, the Remaining Count Probe's prediction $\hat{r}_t$ jumps from 71 to 277 at the token where the model retracts and redoes work — an upward move neither the constant-median nor the exact-countdown baseline can ever produce, since both are monotonically non-increasing by construction. [§sec_4_3]

## Intuition {#intuition}
A countdown timer only counts down. Once it reads 71 seconds left, it can go to 70, 69, and so on — never back up. The two reference predictors this paper compares against work the same way.

The probe reads the model's hidden state instead of a clock. If the model realizes mid-generation that it must redo a step, that recognition can show up as an upward jump in the probe's estimate, even though the true remaining length keeps falling.

## Mechanics {#mechanics}
The probe's prediction $\hat{r}_t$ is read off the hidden state $h_t$ at each position, not off the position $t$ itself, so nothing forces it to decrease as generation proceeds. [§sec_4_3]

| Predictor | Monotonic by construction | Jump at retraction observed |
|---|---|---|
| Constant-median baseline | Yes [§sec_4_3] | No [§sec_4_3] |
| Exact-countdown predictor | Yes [§sec_4_3] | No [§sec_4_3] |
| Remaining Count Probe | No [§sec_4_3] | Yes [§sec_4_3] |

At the token pair marking the model's own retraction, the probe's prediction shifts upward from 71 to 277 while the true remaining count $r_t$ keeps decrementing as it always does — a movement no monotonic-in-$t$ baseline can generate. [§sec_4_3]

The prediction is not accurate in an absolute sense on this completion: at $t=173$ it reads 4.84 against a true $r_t$ of 814. What is trustworthy here is the sign of the change at the retraction token, not the predicted level. [§sec_4_3]

The appendix reports the same upward shift on four more completions, each triggered by a different retraction phrase at a different absolute position, though the authors do not yet aggregate this directional signal against a length-matched control across the eval set — that comparison is flagged as future work. [§sec_4_3]

## The Math {#the-math}
Define the per-position update $\Delta\hat{r}_t = \hat{r}_t - \hat{r}_{t-1}$. Both baselines are monotonic by construction, so $\Delta\hat{r}_t \le 0$ at every position for each of them. [§sec_4_3]

A single position with $\Delta\hat{r}_t > 0$ therefore rules out both baselines as an account of that token, regardless of the jump's size. [§sec_4_3]

At the retraction token, $\Delta\hat{r}_t = 277 - 71 = 206$: a positive update of 206 tokens, which is exactly the kind of move that is impossible for a monotonic predictor and therefore diagnostic on its own. [§sec_4_3]

This sign argument is independent of tracking accuracy. At $t=173$ in the same completion the probe reads 4.84 against a true $r_t = 814$, an error of about 809 tokens — roughly 168 times too low. [§sec_4_3]

So the sign of $\Delta\hat{r}_t$ at the retraction token is informative even though the predicted level is off by two orders of magnitude elsewhere in the same window — the paper is explicit that it is reading the direction of the update, not the value. [§sec_4_3]

Because both baselines are monotonic by construction rather than empirically decreasing, this isn't a statistical unlikelihood — a positive $\Delta\hat{r}_t$ from either one has probability zero, not merely low probability, which is why a single curated example is enough to establish the qualitative claim even though the paper does not yet aggregate it into an eval-set statistic. [§sec_4_3]

## Go Deeper {#go-deeper}
No resource lines are supplied for this concept, so there is nothing to link here.
