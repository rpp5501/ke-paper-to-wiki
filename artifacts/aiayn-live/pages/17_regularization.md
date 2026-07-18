# Regularization
## TL;DR {#tldr}
Regularization is the set of training-time techniques the Transformer uses to keep the model from overfitting and to make its predictions less overconfident. It sits within the broader Training process for the model.

## Intuition {#intuition}
A large sequence-to-sequence model with many parameters can easily memorize training data or become overly certain about its predictions, which hurts how well it generalizes to new sentences. Regularization counteracts this by injecting controlled noise into the network during training (so it can't rely too heavily on any single pathway) and by discouraging the model from assigning full probability mass to a single "correct" token. The result is a model that trains a bit less confidently but performs better on real translation tasks.

## Mechanics {#mechanics}
The authors employ three types of regularization during training [§sec_5_4]. The first, Residual Dropout, is applied to the output of each sub-layer before it is added back to the sub-layer's input and normalized, meaning every attention and feed-forward sub-block has dropout applied right before its residual connection [§sec_5_4]. Dropout is additionally applied to the sums of the token embeddings and positional encodings in both the encoder and decoder stacks, so the very first representations entering the model are also regularized [§sec_5_4]. For the base model configuration, this dropout is applied at a specific rate [§sec_5_4].

## The Math {#the-math}
The local context specifies the mechanism (dropout applied at sub-layer outputs and at the embedding+positional-encoding sums) and names a second technique, label smoothing, applied during training with a given smoothing value, but does not provide the underlying dropout or label-smoothing formulas or the base model's specific numeric hyperparameter values in this excerpt [§sec_5_4]. Label smoothing is noted to hurt perplexity, since it trains the model to be less certain about its outputs, while it improves accuracy and BLEU score [§sec_5_4].

## Go Deeper {#go-deeper}
No research note is available for this concept.
