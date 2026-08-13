I'll rewrite the page, splitting the three overlong paragraphs at their claim boundaries while keeping everything else the same.

# Implementation Details
## TL;DR {#tldr}
- Images are scale-augmented, randomly cropped to 224×224, flipped, and mean-subtracted before training [§sec_3_4].
- Batch normalization sits right after every convolution and before the activation that follows it [§sec_3_4].
- SGD trains with batch size 256, a 0.1 learning rate that steps down ×10 at plateaus, 0.0001 weight decay, and 0.9 momentum — no dropout [§sec_3_4].
- Comparison studies use 10-crop testing; best results average a fully-convolutional network's scores over multiple scales [§sec_3_4].

## Intuition {#intuition}
**A fixed protocol isolates the architecture.** The paper's claims about residual connections only mean something if every network — plain or residual, 18 layers or 152 — trains and tests under the exact same procedure [§sec_3_4].

**That protocol is this section.** The same augmentation, optimizer schedule, and crop-based testing apply to every model, so an accuracy gap is evidence about architecture, not about training luck [§sec_3_4].

## Mechanics {#mechanics}
**Augmentation pipeline.** Training images are resized so their shorter side falls in a randomly sampled range, then a 224×224 patch is cropped from a random location in the image or its horizontal flip, with the per-pixel mean subtracted; standard color augmentation is also applied [§sec_3_4].

**BN placement and initialization.** Batch normalization is inserted right after each convolution and before the activation, following established practice; weights are initialized per prior work and every plain and residual network trains from scratch, so no pretrained features leak into the comparison [§sec_3_4].

**Optimizer.** SGD trains with a 256-image mini-batch, weight decay 0.0001, and momentum 0.9, with dropout omitted in line with prior practice [§sec_3_4].

**Learning-rate schedule.** The learning rate starts at 0.1 and is divided by 10 whenever training error plateaus, rather than on a fixed schedule — so the number of drops depends on when each network's error curve flattens, not on a predetermined iteration count [§sec_3_4].

**Testing protocol.** Comparison studies use the standard 10-crop testing protocol, while the paper's best results instead convert the network to a fully-convolutional form and average its scores across multiple image scales [§sec_3_4].

## The Math {#the-math}
**Why 10-crop testing is exactly 10.** Standard 10-crop testing evaluates 4 corner crops plus 1 center crop from the image, then repeats all 5 on the horizontal flip [§sec_3_4].

That gives 5 × 2 = 10 predictions per image, whose softmax outputs are averaged — trading 10× the inference compute for a variance reduction a single center crop can't get [§sec_3_4].

**What weight decay of 0.0001 does numerically.** Weight decay is a per-step shrinkage: multiplying learning rate 0.1 by decay 0.0001 gives a shrink factor of 0.00001 applied to each weight, before the gradient term is added [§sec_3_4].

That's a tiny nudge per step, but it compounds over the paper's long training runs, pulling weights toward zero unless the gradient signal keeps pushing back — the standard mechanism by which weight decay controls overfitting here [§sec_3_4].

**Learning-rate arithmetic.** Each plateau-triggered ÷10 step takes the rate from 0.1 to 0.01, then to 0.001 — two drops span two orders of magnitude, so by the third rate the model takes steps 1% the size of its first ones [§sec_3_4].

**The 10-crop vs. fully-convolutional choice is a speed/accuracy tradeoff.** 10-crop testing runs 10 separate fixed-size forward passes per image, which is simple but expensive and limited to the crop's exact scale [§sec_3_4].

The fully-convolutional form instead runs the whole resized image through once per scale and averages scores across scales, trading some of that redundancy for scale coverage — which the paper reserves for its best reported results, not routine comparisons [§sec_3_4].

## Go Deeper {#go-deeper}
**Some specific values are missing from the extracted text.** The exact range for the random shorter-side resize, and the multi-scale set used for fully-convolutional testing, are elided in the supplied section — the protocol's shape is clear, but those particular numbers aren't reproducible from this evidence alone [§sec_3_4].

**Why no dropout matters as a comparison point.** Dropout regularizes by design in many CNN training pipelines; omitting it here means whatever depth-related generalization behavior the paper reports for residual networks isn't coming from dropout's noise, leaving batch normalization and weight decay as the active regularizers [§sec_3_4].
