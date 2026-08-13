# Object Detection Generalization
## TL;DR {#tldr}
Swapping ResNet-101 for VGG-16 inside an unchanged Faster R-CNN detector raises PASCAL VOC mAP by roughly 3 points and COCO's mAP@[.5,.95] by 6.0 points, a 28% relative gain [§sec_4_3]. Because only the backbone changes, the improvement is attributable to the learned representation itself, not to the detection method [§sec_4_3].

## Intuition {#intuition}
Faster R-CNN is a detector, but its backbone is a separate classifier network bolted underneath: swap VGG-16 for ResNet-101 and the box-proposal and classification logic stay untouched [§sec_4_3]. That isolates the variable being tested — if detection accuracy rises, the reason is the quality of the features the backbone hands the detector, not a smarter detection algorithm [§sec_4_3].

A stronger classifier on ImageNet does not guarantee a stronger detector: localization, small objects, and occlusion are different challenges than single-label classification. The COCO results here are the paper's evidence that ResNet's advantage carries over anyway [§sec_4_3].

## Mechanics {#mechanics}
The paper reuses Faster R-CNN unmodified as the detection method for both backbones, changing only the network that produces convolutional features [§sec_4_3]. This is a controlled substitution: same detector, same implementation (detailed in the appendix), so any accuracy delta is attributable to the backbone alone [§sec_4_3].

Three experiments compare VGG-16 against ResNet-101 under identical detector settings:
- PASCAL VOC, trained on 07+12, tested on VOC 2007 test, scored at mAP@.5 [tab_6]
- PASCAL VOC, trained on 07++12, tested on VOC 2012 test, scored at mAP@.5 [tab_6]
- MS COCO, scored at both mAP@.5 and the stricter mAP@[.5, .95] [tab_6]

| Benchmark | Train / test | Metric | VGG-16 | ResNet-101 | Source |
|---|---|---|---|---|---|
| VOC 2007 | 07+12 / VOC07 test | mAP@.5 | 73.2 | 76.4 | [tab_6] |
| VOC 2012 | 07++12 / VOC12 test | mAP@.5 | 70.4 | 73.8 | [tab_6] |
| COCO | — | mAP@.5 | 41.5 | 48.4 | [tab_6] |
| COCO | — | mAP@[.5, .95] | 21.2 | 27.2 | [tab_6] |

The result the paper foregrounds is the last row: a 6.0-point gain on COCO's standard metric, which it reports as a 28% relative improvement [§sec_4_3]. The same substitution also underpinned first-place finishes in ImageNet detection, ImageNet localization, COCO detection, and COCO segmentation at ILSVRC & COCO 2015 [§sec_4_3].

## The Math {#the-math}
Take the COCO row the paper highlights: mAP@[.5, .95] rises from 21.2 to 27.2, a difference of 6.0 points [tab_6]. Expressed as a fraction of the VGG-16 baseline, 6.0 / 21.2 ≈ 0.283, which rounds to the paper's reported 28% relative improvement [§sec_4_3].

The same division, run on every row, shows the gain is not uniform:
- VOC07 (07+12): (76.4 − 73.2) / 73.2 ≈ 4.4% relative [tab_6]
- VOC12 (07++12): (73.8 − 70.4) / 70.4 ≈ 4.8% relative [tab_6]
- COCO mAP@.5: (48.4 − 41.5) / 41.5 ≈ 16.6% relative [tab_6]
- COCO mAP@[.5, .95]: (27.2 − 21.2) / 21.2 ≈ 28.3% relative [tab_6]

The relative gain grows metric by metric: about 4–5% on VOC's mAP@.5, 16.6% on COCO's looser mAP@.5, and 28.3% on COCO's mAP@[.5, .95] [tab_6].

One number explains part of this: the VOC baseline is already high, 73.2 and 70.4 out of a 100-point scale, so there is less room left to gain even before the metric changes [tab_6].

That headroom argument only accounts for the VOC-versus-COCO gap, not why COCO's two metrics differ from each other — both start further from 100, yet mAP@[.5, .95] gains almost twice the relative ground that mAP@.5 does [tab_6].

The evidence here does not say why the stricter metric benefits more; that would need per-IoU-threshold breakdowns the paper does not report in this section [§sec_4_3].

## Go Deeper {#go-deeper}
- This concept sits inside the paper's broader claim that residual representations transfer across tasks, not only ImageNet classification — object detection is one instance of that generalization argument [§sec_4_3].
- The Faster R-CNN baseline is the detector held constant across both backbones; its box-proposal and classification heads are detailed in the paper's appendix, not reproduced in this section [§sec_4_3].
- The 2015 ILSVRC & COCO wins — ImageNet detection, ImageNet localization, COCO detection, and COCO segmentation — are named as evidence of the same generalization but not broken down further here [§sec_4_3].
