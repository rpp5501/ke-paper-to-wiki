# Ensemble Results

## TL;DR {#tldr}
The ILSVRC 2015 submission combined six ResNets of different depths into one ensemble, reaching 3.57% top-5 error on the ImageNet test set and beating every previous single-model and ensemble result on record [§sec_4_1].

## Intuition {#intuition}
Averaging several trained networks' predictions cancels out some of each model's individual mistakes, so an ensemble usually scores better than its strongest single member [§sec_4_1].

What stands out about ResNet's ensemble is not the technique itself, which is standard, but how strong the underlying single models already were: even before combining anything, the single 152-layer ResNet outperformed every previously published ensemble [§sec_4_1].

## Mechanics {#mechanics}

**Ensemble composition:** the ILSVRC'15 submission combines six ResNet models of different depths, including only two 152-layer networks at the time of submitting, and reports one top-5 error figure on the test set [§sec_4_1].

**Single model already beats previous ensembles:** the 152-layer ResNet's single-model top-5 validation error of 4.49% is lower than every previously published ensemble result, a comparison the paper draws directly [§sec_4_1].

**Single-model top-5 error on ImageNet val (except † on test):**

| Method | Top-1 err. | Top-5 err. | Evidence |
|---|---|---|---|
| VGG (ILSVRC'14) | - | 8.43%† | [tab_4] |
| GoogLeNet (ILSVRC'14) | - | 7.89% | [tab_4] |
| VGG (v5) | 24.4% | 7.1% | [tab_4] |
| PReLU-net | 21.59% | 5.71% | [tab_4] |
| BN-inception | 21.99% | 5.81% | [tab_4] |
| ResNet-34 B | 21.84% | 5.71% | [tab_4] |
| ResNet-34 C | 21.53% | 5.60% | [tab_4] |
| ResNet-50 | 20.74% | 5.25% | [tab_4] |
| ResNet-101 | 19.87% | 4.60% | [tab_4] |
| ResNet-152 | 19.38% | 4.49% | [tab_4] |

**Test-set result the ensemble is compared against:** the paper reports six methods' top-5 error on the official ImageNet test set, with the six-model ResNet ensemble listed last as "ResNet (ILSVRC'15)" [tab_4].

| Method | Top-5 err. (test) | Evidence |
|---|---|---|
| VGG (ILSVRC'14) | 7.32% | [tab_4] |
| GoogLeNet (ILSVRC'14) | 6.66% | [tab_4] |
| VGG (v5) | 6.8% | [tab_4] |
| PReLU-net | 4.94% | [tab_4] |
| BN-inception | 4.82% | [tab_4] |
| ResNet (ILSVRC'15) ensemble | 3.57% | [tab_4] |

## The Math {#the-math}

**Single model vs. ensemble, same architecture family:** the 152-layer ResNet alone reaches 4.49% top-5 error on the validation split, while the six-model ensemble reaches 3.57% on the test split — different splits, so the gap is a lower bound, not an exact effect size [tab_4].

Treating the two figures as roughly comparable, the ensemble cuts top-5 error by 0.92 percentage points against the single 152-layer model — a 20% relative reduction (0.92 ÷ 4.49) [tab_4].

**Ensemble vs. best non-ResNet baseline, same split:** on the test set, the ensemble's 3.57% compares to BN-inception's 4.82%, the best non-ResNet single model reported — a 1.25-point gap, or 26% relative reduction (1.25 ÷ 4.82) [tab_4].

That 26% relative reduction over the best non-ResNet baseline, delivered by combining six models that individually already beat every prior ensemble, is the headline the 3.57% test number is meant to convey [tab_4][§sec_4_1].

## Go Deeper {#go-deeper}

The ensemble was built under a submission deadline: only two 152-layer networks existed at the time, so the other four members were shallower ResNets included to hit six total rather than because they were the strongest available [§sec_4_1].

The paper frames the ensemble result as confirmation, not the main finding — depth benefits show up in every single-model number in Table 4 before any combining happens, which is why the single 152-layer model already clears the old ensemble bar [§sec_4_1][tab_4].
