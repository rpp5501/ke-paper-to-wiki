# Faster R-CNN Baseline

## TL;DR {#tldr}

Faster R-CNN Baseline swaps VGG-16 for ResNet-50/101 as the backbone of the standard Faster R-CNN detector, without changing the detection pipeline itself. The swap alone raises PASCAL VOC mAP by 3 points and COCO mAP@[.5,.95] by 6.0 points — a 28% relative gain over VGG-16, attributable entirely to better features.

## Intuition {#intuition}

VGG-16 has 13 conv layers followed by fully-connected layers that Faster R-CNN repurposes as the per-region classifier. ResNet has no hidden fc layers, so plugging it in naively would leave the detector without a per-region head.

The fix borrows the Networks on Conv feature maps idea: split ResNet's own conv layers into a shared trunk and a per-region tail, so the region head is still made of convolutions instead of fully-connected layers.

Because the backbone is now deeper and more expressive, the same features that lowered ImageNet classification error also produce sharper, better-localized detections — the detector head stays unchanged, so gains trace directly to representation quality.

## Mechanics {#mechanics}

The shared convolutional trunk uses every layer whose stride on the input image is at most 16 pixels — conv1 through conv4_x, 91 conv layers in total for ResNet-101 [§sec_5].

This trunk plays the same role as VGG-16's 13 conv layers: both backbones produce feature maps at the same total stride of 16 pixels, so the trunk swap is a drop-in replacement [§sec_5].

A region proposal network generating 300 proposals and a Fast R-CNN detection network share this trunk, exactly as in the original Faster R-CNN design [§sec_5].

RoI pooling is performed before conv5_x, and every layer from conv5_x up is applied per region — these layers take over the role VGG-16's fully-connected layers played, implementing the Networks on Conv feature maps idea [§sec_5].

The final classification layer is replaced by two sibling layers, one for classification and one for box regression, matching the standard Faster R-CNN head [§sec_5].

Batch normalization statistics are computed once on the ImageNet training set after pre-training, then frozen throughout detection fine-tuning, turning each BN layer into a fixed linear rescaling [§sec_5].

Freezing BN this way is a memory-saving choice: it avoids recomputing and backpropagating through per-batch statistics during Faster R-CNN training, which is otherwise memory-hungry [§sec_5].

For PASCAL VOC 2007, training uses the 5k VOC 2007 images plus 16k VOC 2012 images (07+12); for PASCAL VOC 2012, training uses 10k+ VOC 2007 images plus 16k VOC 2012 images (07++12) [§sec_5].

COCO training uses an 8-GPU implementation: the RPN step takes a mini-batch of 8 images (one per GPU), and the Fast R-CNN step takes a mini-batch of 16 images [§sec_5].

Both steps train for 240k iterations at a learning rate of 0.001, then 80k more iterations at 0.0001 [§sec_5].

## The Math {#the-math}

| Benchmark | Metric | Gain, ResNet-101 over VGG-16 |
|---|---|---|
| PASCAL VOC 07+12 / 07++12 | mAP@0.5 | +3.0 points [§sec_5] |
| COCO val | mAP@0.5 | +6.9 points absolute [§sec_5] |
| COCO val | mAP@[.5:.95] | +6.0 points absolute, 28% relative [§sec_5] |

On PASCAL VOC, ResNet-101 raises mAP by 3 points over VGG-16 — the entire gain is attributed to improved features, since the detection pipeline is otherwise unchanged [§sec_5].

**Reading the COCO improvement two ways:** ResNet-101 improves mAP@[.5,.95] by 6.0 points over VGG-16 in absolute terms [§sec_5].

As a ratio, that 6.0-point gain works out to a 28% relative improvement over the VGG-16 baseline — back-solving, 6.0 is 28% of the baseline, which implies a VGG-16 baseline of roughly 6.0 / 0.28 ≈ 21.4 mAP and a ResNet-101 result of roughly 27.4 mAP [§sec_5].

**Checking whether the gain survives stricter IoU thresholds:** PASCAL's mAP@0.5 uses one loose overlap threshold, while COCO's mAP@[.5,.95] averages over ten thresholds from 0.5 to 0.95, so it penalizes poor localization far more heavily [§sec_5].

The paper reports mAP@0.5's absolute increase as 6.9 points, almost matching mAP@[.5,.95]'s 6.0-point increase — a ratio of 6.0/6.9 ≈ 0.87, meaning the gain barely shrinks under the stricter, localization-heavy metric [§sec_5].

**A boundary case the numbers expose:** if ResNet-101 only helped recognition without improving localization, the mAP@[.5,.95] gain should shrink sharply relative to mAP@0.5's, since stricter thresholds punish misaligned boxes that looser ones still count as correct [§sec_5].

That the two gains stay close instead confirms the paper's own reading: a deeper backbone improves both recognition and localization together, not recognition alone [§sec_5].

## Go Deeper {#go-deeper}

This baseline is the entry point for the paper's Object Detection Generalization story: it establishes that a straight backbone swap, with no detector redesign, already moves the needle, which is what the Detection Improvements that build on it then try to extend further.

The experiments were run at the time of the ILSVRC & COCO 2015 detection competitions, using ResNet-50/101 as the two backbone depths tested [§sec_5].
