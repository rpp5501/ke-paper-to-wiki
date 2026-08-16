# Challenges and Future Directions

## TL;DR {#tldr}
Three gaps remain open: no general classification of which symmetries an arbitrary architecture has, no rigorous symmetry-based account of why flat minima generalize or why independent runs converge to similar solutions, and no theory of when permutation-based model merging succeeds as architectures grow larger and more heterogeneous [§sec_7].

## Intuition {#intuition}
Everything covered so far was built architecture by architecture: permutation and scaling symmetries proven for specific layer types, alignment algorithms tuned to specific network families. That case-by-case foundation is solid but incomplete.

It tells you what's true for the architectures already analyzed, not what's true in general — like knowing several symmetries of a shape without knowing whether you've found its whole symmetry group.

The three challenges below are the same gap at different scales: do we know the full symmetry group, do we know why that group matters for learning, and do we know how far the practical tricks built on it will travel.

## Mechanics {#mechanics}

**Classifying the symmetry group is still open.** No general theory yet determines the complete symmetry group of an arbitrary deep network architecture, so even the basic questions of whether that group is finite and whether it can be fully enumerated remain unresolved for architectures beyond the cases already analyzed [§sec_7][S2].

**The link from symmetry to generalization is asserted more than proven.** Two long-standing empirical observations — that flat regions of the loss landscape tend to generalize well, and that independently trained networks converge to functionally similar solutions — still lack a rigorous symmetry-based explanation, and sit alongside other statistical-mechanical phenomena of deep networks that remain unexplained [§sec_7][S1].

**Permutation-based model merging has an empirical scope, not a proven one.** Practitioners can align two independently trained networks by finding the permutation that moves one into the same region of the loss level set as the other, letting the pair be merged or interpolated; this succeeds well in practice mainly for moderate-width MLPs and CNNs [§sec_7][S3].

**How far that success generalizes is the open question.** A general theory of when permutation alignment succeeds, and of how it scales to larger and more heterogeneous architectures than moderate-width MLPs and CNNs, is still underdeveloped [§sec_7][S3].

| Challenge | What's established | What's missing |
|---|---|---|
| Symmetry group structure | Groups known for specific layer types and architectures | No classification of completeness/finiteness for arbitrary architectures [§sec_7][S2] |
| Symmetry ↔ generalization | Flat minima and cross-run functional similarity are observed empirically | No rigorous symmetry-based account of either [§sec_7][S1] |
| Permutation alignment | Works well on moderate-width MLPs/CNNs | No general theory of when/why it succeeds or how it scales [§sec_7][S3] |

## The Math {#the-math}

Consider where permutation alignment's empirical success actually stops, since that boundary shows what the missing theory would need to supply [§sec_7][S3].

On a moderate-width MLP or CNN, two independently trained networks can be aligned into the same basin by solving for the permutation matrices that best match one network's neurons to the other's, and the aligned pair then sits close enough on the loss level set to interpolate or merge without a large loss barrier [§sec_7][S3].

That success is reported specifically for moderate width: the redundancy permutation symmetry captures, which neuron computes which feature, apparently accounts for most of the functional difference between the two runs at that scale [§sec_7][S3].

The open boundary is what happens as width grows or the architecture becomes heterogeneous: nothing in the evidence says permutation-only matching keeps capturing the dominant source of difference between two runs at larger or mixed-layer scale, and no general theory yet states the condition under which it does [§sec_7][S3].

The same boundary appears one level up, in the symmetry group itself: proving a group finite and enumerable for one layer type does not establish that composing more such layers keeps the group finite or classifiable, which is exactly the open completeness and finiteness question [§sec_7][S2].

## Go Deeper {#go-deeper}

- [Git Re-Basin: Merging Models modulo Permutation Symmetries](https://arxiv.org/abs/2209.04836) — the concrete permutation-alignment method this page's boundary case is about, including its own discussion of where the approach breaks down. Start here.
- [git-re-basin (official code and figures)](https://github.com/samuela/git-re-basin) — the README's interpolation plots show what "moving along a loss level set via permutation" looks like, which is easier to grasp from the figures than from the equations alone.
- [The Modern Mathematics of Deep Learning](https://arxiv.org/abs/2105.04026) — surveys what is and isn't rigorously proven about deep network geometry and optimization, useful for gauging how far a formal account of parameter-space symmetry still has to go.
- [Statistical Mechanics of Deep Learning](https://doi.org/10.1146/annurev-conmatphys-031119-050745) — reviews the unresolved statistical-physics-style questions about loss landscapes and generalization that a symmetry-based theory would need to explain.
