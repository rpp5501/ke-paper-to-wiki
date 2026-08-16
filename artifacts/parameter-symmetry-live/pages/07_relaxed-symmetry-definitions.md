Fixing the two issues: splitting the six over-length paragraphs at their natural claim boundaries, and rebuilding The Math tier around the containment argument and the Ainsworth/SGD boundary case instead of reporting an absent equation.

# Relaxed Definitions of Symmetry

## TL;DR {#tldr}

Exact functional symmetry requires a parameter transformation to preserve a network's output on every possible input — a bar almost no useful transformation actually clears.

Godfrey et al. relax this into a hierarchy: symmetries that preserve only the loss, only the output on the actual data, or only the output in a distributional sense over the data manifold [S1].

Each level strictly contains the one before it, so the transformations that explain real trained networks live in the weaker tiers, not in exact functional symmetry.

## Intuition {#intuition}

Picture two students compared on an exam. The strictest standard says they must give an identical answer to every question that could ever be asked — that is functional symmetry, and it is almost impossible to satisfy in practice.

A looser standard checks only the final score: different answers can add up to the same grade — that's loss symmetry.

Looser still, data-dependent symmetry checks agreement only on the exam actually given, and distributional symmetry checks agreement only on average across exams drawn from a similar syllabus.

This is why researchers can call an SGD-trained network "approximately permutation invariant" without meaning it holds for every conceivable input.

## Mechanics {#mechanics}

Godfrey et al. formalize the relaxation as a four-level hierarchy, each level defined by what must stay invariant under a parameter transformation and over what set of inputs it must hold [S1].

| Level | Must preserve | Must hold over | Grounding |
|---|---|---|---|
| Functional | The full output map $f_w = f_{w'}$ | Every input in the domain | The exact case treated in Functional Neural Network Symmetry [S1] |
| Loss | The scalar loss value $L(w) = L(w')$ | Every input, but only through the loss | Outputs can differ while the loss they produce still matches [S1] |
| Data-dependent | Output equality | Only the finite training or test set actually used | Two weight settings that agree on every observed example, not necessarily elsewhere [S1] |
| Distributional | Output equality in a statistical sense | The data distribution $P(x)$, not pointwise | SGD solutions are "approximately" permutation invariant on the data manifold [S2] |

The note states this explicitly: each relaxed notion strictly generalizes the one listed before it, so the set of transformations counted as symmetries grows monotonically from functional through loss and data-dependent to distributional [S1].

The relaxation is not academic bookkeeping: it is what licenses claims researchers actually make about trained networks [S1].

Ainsworth et al. permute one network's neurons to align it with an independently trained network. That collapses the loss barrier between them on real data, even though the two functions are not exactly equal everywhere [S3].

That gap between "loss barrier collapses" and "functions are equal everywhere" is exactly the space the relaxed definitions were built to describe: a transformation can be a data-dependent or distributional symmetry without ever being a functional one [S1].

## The Math {#the-math}

Functional symmetry is the strongest condition: $f_w(x) = f_{w'}(x)$ must hold for every $x$ in the input domain, including inputs no training process ever sees [S1].

That statement implies the loss-level one automatically: if outputs match at every $x$, then $L(w) = L(w')$ for any loss function computed from those outputs, since loss is a function of the output, not an independent constraint [S1].

Matching everywhere is sufficient but not necessary for a transformation to be useful, and the gap below functional symmetry is where such transformations live. Ainsworth et al.'s permutation, which aligns one independently trained network's neurons with another's, collapses the loss barrier between them on real data without making the two functions identical at every input [S3].

Distributional symmetry weakens the requirement further, from equality at every $x$ to equality with probability close to 1 under the data distribution: $\Pr_{x \sim P}[f_w(x) = f_{w'}(x)] \approx 1$ rather than $= 1$ [S2].

That distinction is not vacuous: a network can disagree with another at inputs where $P$ assigns negligible mass — off-manifold points a trained model rarely encounters — while still counting as distributionally symmetric, which is exactly why SGD-trained networks are called approximately permutation invariant despite not being invariant pointwise [S2].

## Go Deeper {#go-deeper}

- [On the Symmetries of Deep Learning Models and Their Internal Representations](https://arxiv.org/abs/2205.14258) — the source of the four-level hierarchy this page describes (functional, loss, data-dependent, distributional); start here for the formal definitions.
- [The Role of Permutation Invariance in Linear Mode Connectivity of Neural Networks](https://arxiv.org/abs/2110.06296) — argues why the data-dependent or distributional notion, not the exact functional one, is what actually explains SGD solutions.
- [Git Re-Basin: Merging Models modulo Permutation Symmetries](https://arxiv.org/abs/2209.04836) — the concrete visual demonstration: permutation alignment collapses the loss barrier on real data without the networks being functionally identical everywhere.
