# Estimation Step (MM Optimization)
## TL;DR {#tldr}
For every candidate target class, this step searches for the input that makes the network most confidently prefer that class over all others, and how large that preference gets is the class's "MM statistic." It is the estimation half of MM-BD's Detection Procedure, feeding the largest such statistic into the inference step that decides whether a backdoor exists and which class it targets.

## Intuition {#intuition}
Instead of guessing what a hidden trigger pattern looks like, the method asks a simpler question for each class: if an attacker could push any valid input toward this class, how big a margin could they force between this class's score and the runner-up? A class that has been backdoored will have a secret shortcut baked into the network, so its best-achievable margin will be unusually large compared to ordinary, un-tampered classes. This reframes backdoor detection as an optimization problem per class rather than a pattern-matching problem, which is why the same procedure works regardless of what the actual trigger looks like — a patch, a blend, a warp, or anything else.

## Mechanics {#mechanics}
For each putative target class, the estimation step performs gradient ascent on the margin objective, starting from a randomly initialized input and repeatedly stepping uphill, projecting the iterate back onto the valid input domain after every step so it never leaves the space of legitimate inputs (e.g., the pixel box for images) [§sec_3_2]. Convergence of this procedure is guaranteed whenever the logit function is continuous and the domain is compact, which holds for standard image classifiers operating on a bounded pixel range [§sec_3_2]. Because the underlying objective is non-convex, a single ascent run can get stuck in a local optimum, so the procedure is repeated from multiple random initializations — for images, pixel values drawn uniformly at random — and only the best solution found across restarts is kept for that class [§sec_3_2]. This design is what decouples the method from any assumption about the backdoor pattern's form: unlike prior reverse-engineering defenses (REDs) that presume an embedding function for the trigger, this optimization makes no such assumption and needs no clean samples from source classes, so it remains effective even when a backdoor's source classes are a small or unknown subset of all classes [§sec_3_2]. Mechanically, the projected ascent loop is the same primitive used to craft adversarial examples under a box constraint via projected gradient descent, just run in the ascent direction and per-class rather than per-example [S3].

## The Math {#the-math}
The core optimization problem solved once per putative target class $c$ maximizes the gap between that class's logit and the best competing logit over the constrained input domain [eq_2]:

$$
\maximize_{{\bf x}\in{\mathcal X}} \quad g_c({\bf x}) - \max_{k\in{\mathcal Y}\setminus c} g_{k}({\bf x})
$$ [eq_2]

Here $g_c$ and $g_k$ are the network's logit outputs for classes $c$ and $k$, $\mathcal{Y}\setminus c$ is the set of all other classes, and $\mathcal{X}$ is the compact input domain (e.g., $[0,1]^{H\times W\times C}$ for color images), which is exactly the set the projection step clips back onto after each gradient ascent update [§sec_3_2][S1]. The resulting optimal value is the MM statistic for class $c$, and the largest statistic across all classes is later compared, via an order-statistic p-value, against a fitted null distribution of the remaining classes' statistics in the separate detection-inference step [eq_3]; that comparison lies outside this estimation step itself but is the reason the estimation step is run once per class rather than once overall [§sec_3_2].

## Go Deeper {#go-deeper}
- **MM-BD paper (Sec. 3.2, arxiv.org/abs/2205.06900)** — primary source; gives the exact optimization problem, the projection domain, and the convergence guarantee this page describes.
- **Madry et al., "Towards Deep Learning Models Resistant to Adversarial Attacks" (arxiv.org/abs/1706.06083)** — the canonical projected gradient method this estimation step's ascent-and-clip mechanics are borrowed from, just run toward higher confidence instead of toward misclassification.
- **Bubeck, "Convex Optimization: Algorithms and Complexity" (arxiv.org/abs/1405.4980)** — background theory on projection operators onto compact sets, cited by the MM-BD authors themselves as the basis for the projection step's guarantees.
