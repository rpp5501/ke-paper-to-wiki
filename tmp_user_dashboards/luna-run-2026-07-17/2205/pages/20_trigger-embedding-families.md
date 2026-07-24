# Trigger-Embedding Families

## TL;DR {#tldr}
The experiments include additive patterns, patch replacement patterns, and blended patterns, while MM-BD uses none of these mechanisms as a detection assumption.

## Intuition {#intuition}
A trigger may be a faint watermark, a small pasted object, or a transparent overlay. A detector tied to one visual recipe can miss the others; MM-BD instead looks for the model-side consequence shared by their repeated use.

## Mechanics {#mechanics}
The paper describes additive perturbations, local patch replacement, and blending with a mask and factor. Its experiments also include chessboard, 1-pixel, BadNet, unicolor, and blend variants [§sec_1]. The detector optimizes over images directly, so it need not decide which embedding family generated a suspicious model [§sec_1].

## The Math {#the-math}
The patch abstraction is $$\tilde{\mathbf{x}}=(1-\mathbf{m})\odot\mathbf{x}+\mathbf{m}\odot\mathbf{u}$$ [§sec_1]. A blended pattern is represented as $$\tilde{\mathbf{x}}=(1-\alpha\mathbf{m})\odot\mathbf{x}+\alpha\mathbf{m}\odot\mathbf{u}$$ [§sec_1].

## Go Deeper {#go-deeper}
- Pattern-Agnostic Attack Signature explains the invariant MM-BD uses.
- Classical Poisoning Mechanism explains how any family becomes training evidence.
- Empirical Scope and Failure Modes reports cross-pattern performance.
