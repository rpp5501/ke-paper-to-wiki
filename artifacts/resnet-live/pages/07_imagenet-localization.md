I found no existing file for this concept — this is a standalone regeneration, so I'll return the corrected page directly.

# ImageNet Localization
## TL;DR {#tldr}

A per-class Region Proposal Network built on ResNet-101 turns a classifier into a localizer: it drops the oracle (ground-truth-class) top-5 localization error from VGG's 33.1% to 13.3%, and an R-CNN refinement stage plus ensembling brings the final test error to 9.0% — a 64% relative cut versus the ILSVRC'14 winner.

## Intuition {#intuition}

Localization has two separable jobs: naming the object and boxing it. This method keeps them separate — a classifier picks the class, and a class-specific RPN proposes boxes tuned to that class rather than a generic "object" box shared across categories.

The refinement stage borrows R-CNN's older, region-centric training instead of the newer Fast R-CNN. ImageNet images usually have one dominant object, so Fast R-CNN's overlapping proposals give the optimizer too little variation to learn from.

## Mechanics {#mechanics}

**Two-stage pipeline:** image-level classifiers first predict the class labels, then the localization algorithm predicts bounding boxes conditioned on those predicted classes [§sec_7].

**Per-class RPN architecture:** the RPN ends in two sibling 1×1 convolutional layers — a 1000-d classification layer (object-or-not per class) and a 10004-d box-regression layer (4 coordinates × 1000 classes), unlike prior category-agnostic RPNs [§sec_7].

**Anchors and augmentation:** as in the classification training, boxes are regressed relative to multiple translation-invariant anchor boxes at each position, with random 224×224 crops used for augmentation [§sec_7].

**Fine-tuning setup:** the network is pretrained for classification, then fine-tuned for localization with a mini-batch of 256 images; 8 anchors are sampled per image at a 1:1 positive-to-negative ratio to keep negatives from dominating [§sec_7].

**Fully convolutional testing:** at test time the network is applied to the whole image fully-convolutionally rather than on fixed crops [§sec_7].

**Why R-CNN over Fast R-CNN:** ImageNet images usually contain one dominant object, so proposal regions overlap heavily and share near-identical RoI-pooled features. Fast R-CNN's image-centric batches would carry too little variation for stochastic training, so refinement instead uses the older, region-centric R-CNN [§sec_7].

```algorithm
title: R-CNN refinement of per-class RPN proposals
lines:
  - code: "boxes = per_class_RPN(image, gt_class)"
    intent: "The trained per-class RPN produces class-dependent proposal boxes for the ground-truth class during training [§sec_7]"
  - code: "top200 = top_scored(boxes, k=200)"
    intent: "Only the 200 highest-scored proposals per image become R-CNN training samples, keeping the region-centric batch small [§sec_7]"
  - code: "crop = warp(image, top200, size=224)"
    intent: "Each proposal is cropped and warped to 224x224, matching the classification network's input, as in the original R-CNN [§sec_7]"
  - code: "cls, box = R_CNN(crop)"
    intent: "A per-class fc head scores the region and refines its box, fine-tuned RoI-centric with batch size 256 [§sec_7]"
  - code: "score', box' = update(boxes, cls, box)"
    intent: "At test time, R-CNN rescoring and re-regressing the RPN's top-200 boxes per class is what drops top-5 error from 14.4% to 10.6% [§sec_7][tab_10]"
```

**Localization results:**

| Method | Network | Testing | LOC error on GT class | Top-5 LOC error (predicted class) | Evidence |
|---|---|---|---|---|---|
| VGG (ILSVRC'14) | VGG-16 | 1-crop | 33.1% | — | [tab_10] |
| RPN | ResNet-101 | 1-crop | 13.3% | — | [tab_10] |
| RPN | ResNet-101 | dense | 11.7% | — | [tab_10] |
| RPN | ResNet-101 | dense | — | 14.4% | [tab_10] |
| RPN+R-CNN | ResNet-101 | dense | — | 10.6% | [tab_10] |
| RPN+R-CNN | ensemble | dense | — | 8.9% | [tab_10] |

## The Math {#the-math}

**Oracle-setting reduction:** replacing VGG's pipeline with the per-class ResNet-101 RPN cuts single-crop, ground-truth-class error from 33.1% to 13.3% — a 19.8-point absolute drop, or a 2.49× reduction in error rate [tab_10].

**Multi-scale testing gain:** dense, multi-scale evaluation of the same ResNet-101 RPN further lowers the oracle error from 13.3% to 11.7%, a gain from testing protocol alone, separate from the architecture change above [tab_10].

**Cost of predicted classes:** swapping the ground-truth class for ResNet-101's own predicted class raises top-5 error from 11.7% to 14.4% — a 2.7-point gap attributable to the classifier's 4.6% top-5 classification error propagating into wrong boxes [tab_10][§sec_7].

**R-CNN refinement gain:** adding the R-CNN stage drops top-5 error from 14.4% to 10.6%, a 3.8-point absolute improvement — about a 26% relative reduction ((14.4−10.6)/14.4) from rescoring and re-regressing the RPN's own top-200 proposals [tab_10].

**Final result versus prior state of the art:** the ensembled system reaches 9.0% top-5 test error against VGG's 25.3% (the ILSVRC'14 winner), a (25.3−9.0)/25.3 ≈ 64% relative reduction — matching the paper's own reported figure [tab_11][§sec_7].

## Go Deeper {#go-deeper}

This localization method is a direct application of the Faster R-CNN RPN framework, adapted from its original category-agnostic design into a per-class form — trading a shared 2-way classifier and 4-d box head for 1000 independent versions of each.

It builds directly on the paper's ImageNet classification results: the same ResNet-101 backbone that achieves 4.6% top-5 classification error is reused, via fine-tuning, as the localization backbone, so a classification mistake becomes a localization mistake too — exactly what the 11.7%→14.4% gap shows.

The R-CNN-over-Fast-R-CNN choice foreshadows a broader lesson beyond ImageNet: proposal diversity, not just proposal quality, matters for how well a detector's second stage can be trained by stochastic gradient descent.
