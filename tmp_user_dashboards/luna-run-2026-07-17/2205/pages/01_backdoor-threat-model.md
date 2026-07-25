# Backdoor Threat Model

## TL;DR {#tldr}
The paper studies a trained image classifier that behaves normally on clean inputs but routes triggered inputs from one or more source classes to an attacker-chosen target class.

## Intuition {#intuition}
The attack is like hiding a secret instruction in a model's training history. A normal image should be recognized by its ordinary content, but the same small cue repeated during poisoning becomes a shortcut that overrides that content later.

## Mechanics {#mechanics}
The paper distinguishes basic, advanced, and adaptive attackers. The basic attacker poisons data without seeing the original training set or controlling training; advanced attackers may use surrogate data or training control; an adaptive attacker also knows MM-BD and optimizes against it [§sec_1]. The defender receives a trained classifier after training and wants detection first, followed by mitigation if replacement is unavailable [§sec_1].

## The Math {#the-math}
A classical backdoor aims for clean correctness and triggered misclassification simultaneously: $$f(\mathbf{x})=y_{\mathrm{true}},\qquad f(\tilde{\mathbf{x}})=t$$ [§sec_1]. The paper's threat model makes $t$ an attacker-selected target and allows an arbitrary number of source classes [§sec_1].

## Go Deeper {#go-deeper}
- Classical Poisoning Mechanism gives the training-time construction.
- Attacker Capability Ladder compares the three attacker regimes.
- Empirical Scope and Failure Modes records where the assumptions become fragile.
