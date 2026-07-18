# Attribute Inference Preliminaries

## TL;DR {#tldr}
This concept lays the groundwork for the paper's central topic: attacks that try to guess a hidden ("sensitive") attribute of a person's record just by querying a trained model. It defines the basic vocabulary — the target record, its non-sensitive fields, the model being attacked, and the sensitive value the adversary wants to recover — and introduces the idea that an attack's success can be measured, and can differ sharply across subgroups of the population. It sits as a foundational piece of the broader **Disparate Privacy Vulnerability** work and depends on first understanding the **Attack Threat Model** (what the adversary is assumed to know and be able to do).

## Intuition {#intuition}
Imagine a machine learning model trained on people's records, where one field — say, an income bracket or a health status — is meant to stay private. An attribute inference attack is like a guessing game: the adversary doesn't have that private field, but they can ask the model questions (or peek at its internals) and use the answers to make an educated guess. This section sets up that game formally, and also introduces a fairness-flavored question that the rest of the paper builds on: is this guessing game equally easy for everyone, or are some people's private attributes much easier to expose than others'?

## Mechanics {#mechanics}
The setup starts from a record whose non-sensitive portion is observable and whose sensitive attribute value is the attack's target; the adversary's goal is to predict that sensitive value using the target model, and some attack variants additionally assume access to auxiliary data beyond what the model exposes [§sec_2].

One family of techniques, introduced as CSMIA, works by querying the model repeatedly with the record's non-sensitive fields combined with each candidate sensitive value in turn, collecting the model's predicted class label and confidence score for each query; if exactly one candidate value causes the model to output the correct class label, the adversary outputs that candidate, and when multiple or zero candidates do so, the adversary breaks ties using the confidence scores (highest confidence when multiple candidates match, lowest confidence when none do) [§sec_2].

A second technique, LOMIA, reuses the same querying idea but ignores confidence scores entirely: it builds a labeled attack dataset only from records where exactly one candidate value produced a correct prediction, using the non-sensitive fields as input and the recovered sensitive value as the training label, then trains a separate attack model on that dataset to infer sensitive values for the remaining records [§sec_2].

A related variant follows the same LOMIA-style dataset construction but substitutes a different feature representation as input before training the attack model, showing that the attack framework is not tied to a single choice of input features [§sec_2].

The paper also describes a whitebox attack that does not rely on querying the model at all: it identifies the ten neurons in the target MLP most correlated with the sensitive attribute, computes a weighted sum of those neurons' activations for a given record, and predicts the sensitive value of interest whenever that sum exceeds a threshold — directly exploiting internal model structure rather than input-output behavior [§sec_2].

Finally, this section formalizes what it means for an attack to be *disparately* vulnerable across a population, which is the property the rest of the paper investigates rather than a specific attack algorithm [§sec_2].

## The Math {#the-math}
The local context for this concept describes the disparity definition in prose rather than as a labeled display equation, so no `[eq_N]` entries are reproduced here; the definition itself is captured below using its section anchor [§sec_2].

Formally, given an attack model, a target dataset, and an attack algorithm, the paper defines an *attack success rate* function measuring how well the algorithm recovers sensitive values when applied to the model and a given subset of the data; a model is said to be disparately vulnerable to the attack if there exist two disjoint subsets of the target dataset whose attack success rates differ by more than a fixed threshold, meaning the gap is large enough not to be dismissed as negligible noise [§sec_2].

## Go Deeper {#go-deeper}
No research note is attached to this concept. For further context within the wiki itself: see **Disparate Privacy Vulnerability** (the parent concept this preliminary material supports) and **Attack Threat Model** (the prerequisite defining what the adversary is assumed to know before these attacks can be launched).
