# Vanishing/Exploding Gradients

## TL;DR {#tldr}

Backpropagation computes each layer's gradient by multiplying local derivatives together across every layer between it and the loss. Vanishing/exploding gradients is the failure mode where this chain of multiplications shrinks toward zero or blows up toward infinity as depth grows, stalling training before it starts [§sec_1].

The ResNet paper treats this as a solved problem for the networks it studies — normalized initialization and intermediate normalization layers let SGD converge for tens of layers — and argues that a second, distinct obstacle (degradation) appears once convergence begins [§sec_1].

## Intuition {#intuition}

Picture backpropagation as a message passed backward through the network, one layer at a time. Each layer relays the message by multiplying it by a local factor — roughly, how sensitive that layer's output is to its input [§sec_1].

If that factor is reliably below 1, the message shrinks a little at every relay. Repeat it across dozens of layers and the message that reaches the earliest layers is negligibly small: those layers get almost no signal about how to update, so training stalls [§sec_1].

If the factor is reliably above 1, the opposite happens — the message grows at every relay until it overflows, and updates become too large and unstable to converge [§sec_1]. Either direction hampers convergence "from the beginning," before the network has had any chance to fit the data [§sec_1].

## Mechanics {#mechanics}

Deep networks compose many nonlinear layers, and gradient descent needs the gradient of the loss with respect to every layer's parameters, not just the last one. The chain rule computes each of those gradients as a product of local derivatives, one per layer, chained back from the loss to that layer [§sec_1].

**Depth is what makes this dangerous:** a shallow network only chains a few of these factors, so their product stays close to a reasonable range whether it drifts up or down [§sec_1].

A very deep network chains tens of them, and even a mild, consistent bias in one direction compounds across every layer in the chain [§sec_1].

The paper reports that this instability has been "largely addressed" for the depths it studies, specifically by normalized initialization and intermediate normalization layers. Those techniques constrain each layer's local factor so the chained product neither collapses nor explodes, which is what lets SGD with backpropagation start converging for networks tens of layers deep [§sec_1].

Convergence starting is not the same as convergence succeeding. Once deep networks are able to start converging, the paper documents a separate problem: accuracy saturates and then degrades as depth keeps increasing, even though the network is optimizing rather than stalling [§sec_1].

Figure fig_1 shows this directly on CIFAR-10 — the degradation is not the vanishing/exploding gradient signature, since it appears in networks that are already converging [§sec_1].

```figure
id: fig_1
caption: A 56-layer plain net has *higher* training error than a 20-layer one — the opposite of what vanishing/exploding gradients alone would predict once both are converging [§sec_1]
```

## The Math {#the-math}

Model the chained backward-pass factor crudely as $c^L$, where $c$ is a representative per-layer derivative magnitude and $L$ is depth — this is the multiplicative structure the paper's text describes when it names vanishing/exploding gradients [§sec_1].

At $c=0.9$ and $L=50$: $0.9^{50} \approx 0.0052$ — the signal reaching an early layer is under 1% of its original size [§sec_1].

At $L=20$ the same $c$ gives $0.9^{20} \approx 0.12$, over 20 times larger than the $L=50$ result — depth alone, not a change in $c$, produces that gap [§sec_1].

That gap is exponential rather than linear because $c^L$ is a power, not a sum: doubling depth roughly squares the shrink factor [§sec_1].

The exploding case is symmetric — $c=1.1$ gives $1.1^{50} \approx 117$, a signal grown two orders of magnitude rather than vanished [§sec_1].

Neither extreme depends on what the network is trying to learn; both follow from depth alone once $c$ drifts from 1, which is why the paper's fix is architectural — normalized initialization and intermediate normalization layers — rather than something more data or more epochs could repair [§sec_1].

## Go Deeper {#go-deeper}

This concept sits upstream of the Degradation Problem, but the two are not the same failure [§sec_1].

Vanishing/exploding gradients prevents a deep network from starting to converge at all; degradation shows up after that problem is fixed, in networks that are converging but still getting worse with added depth [§sec_1].

The paper's evidence for treating them as separate rests on fig_1: a 56-layer plain network has *higher training error* than its 20-layer counterpart, not just higher test error, which rules out both underfitting-by-gradient-stalling and overfitting as explanations [§sec_1].

Residual learning (fig_2) is the paper's answer to degradation, not to vanishing/exploding gradients: the identity shortcut is motivated by giving deep stacks an easy path to the identity mapping, not by rescaling backward-pass magnitudes [§sec_1].

```figure
id: fig_2
caption: The shortcut this paper adds is an identity path around a few stacked layers — a separate fix from the normalization that already addresses vanishing/exploding gradients [§sec_1]
```
