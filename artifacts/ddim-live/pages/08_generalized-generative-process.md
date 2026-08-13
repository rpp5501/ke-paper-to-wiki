# Generalized Generative Processes

## TL;DR {#tldr}

- A single trained noise-prediction network already solves the shared training objective for every non-Markovian forward process in the sigma-parametrized family, including the original Markovian DDPM process as one special case.
- Because retraining is unnecessary, the only design choice left is picking sigma to get a generative process that samples the way you want.

## Intuition {#intuition}

Think of the noise-prediction network as a single trained engine and sigma as a dial you turn afterward. The engine does not need to be rebuilt for a new dial setting — each setting just drives a different generative process built from the same trained parts.

That reframes the whole problem. Instead of asking "how do I train a better sampler," the question becomes "which dial setting produces the samples I actually need," since the training work is already done.

## Mechanics {#mechanics}

The paper's variational objective is not exclusive to the Markovian inference process used in prior DDPM work: the same objective is simultaneously the training objective for a whole family of non-Markovian forward processes parametrized by sigma. [§sec_4]

**Why reuse works:** sigma only selects which non-Markovian forward process the shared objective describes; the objective's optimum does not depend on that choice. A network optimizing it for one sigma is already optimizing it for every other. [§sec_4]

**The boundary this creates:** one member of this family is exactly the Markovian process already trained in prior DDPM work, recovered at one particular setting of sigma. [§sec_4]

Every other setting of sigma gives one of the non-Markovian processes this paper introduces, and each one is still solved by that same pretrained network — no retraining required. [§sec_4]

**What this changes for practitioners:** because no new network is needed, choosing a generative process becomes a sampling-time decision — something to search over after training finishes, rather than a reason to retrain. [§sec_4]

## The Math {#the-math}

The local evidence for this concept gives no display equation, so the argument below is built directly from the reuse claim itself. [§sec_4]

Because sigma never appears in what the network is trained to predict, sweeping it from the value that reproduces the original process to any other value adds no training cost — only inference-time computation changes. [§sec_4]

**Counterexample check:** if changing sigma also changed which network minimizes the objective, reuse would break — each sigma would need its own trained model, erasing the speedup this section relies on. [§sec_4]

## Go Deeper {#go-deeper}

- **Unified Variational Inference Objective** (prerequisite) — defines the full sigma-parametrized family this section reuses a single network across.
- **Accelerated Generation Processes** — builds on this reuse property to skip sampling steps without retraining.
- **Relevance to Neural ODEs** — connects the deterministic end of this family to ODE-solver intuitions.
- **DDIM Sampling Update Equation** — the concrete update rule for the deterministic member of this family.
