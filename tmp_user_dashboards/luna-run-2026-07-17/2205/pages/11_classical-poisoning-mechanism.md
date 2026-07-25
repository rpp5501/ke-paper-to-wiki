# Classical Poisoning Mechanism

## TL;DR {#tldr}
A classical backdoor poisons training by embedding a common pattern in source-class samples, relabeling them to a target class, and mixing them into the training set.

## Intuition {#intuition}
The attacker teaches the model a second rule: ordinary content maps normally, but the repeated mark overrides that content. Because only a small portion of training data needs the mark, clean behavior can remain apparently intact.

## Mechanics {#mechanics}
The paper's classical protocol collects source-class samples, embeds the same pattern, relabels those samples to the target, and inserts them for poisoning [§sec_1]. The trained classifier is evaluated with clean accuracy and attack success rate, so stealth means preserving the first while increasing the second [§sec_1].

## The Math {#the-math}
For an additive trigger $\mathbf{v}$, one image-level abstraction is $$\tilde{\mathbf{x}}=[\mathbf{x}+\mathbf{v}]_c$$ [§sec_1]. The target behavior can be summarized as $f(\mathbf{x})=y$ on clean inputs but $f(\tilde{\mathbf{x}})=t$ on triggered inputs [§sec_1].

## Go Deeper {#go-deeper}
- Trigger-Embedding Families compares additive, patch, and blend mechanisms.
- Backdoor Threat Model places poisoning in the attacker capability ladder.
- Pattern-Agnostic Attack Signature explains why MM-BD does not reconstruct the poison.
