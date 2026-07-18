# Backdoor Pattern (BP) Type Settings

## TL;DR {#tldr}
This concept defines the experimental configuration used to test UnivBD (Universal Backdoor Detector) against diverse backdoor attacks. It spans three families of backdoor patterns — Additive Perturbation, Patch Replacement, and Blending — combined with different choices of how many classes an attack targets as sources, so the detector's generality can be evaluated rather than its performance on a single narrow attack recipe.

## Intuition {#intuition}
A detector that only works against one kind of backdoor trigger isn't very useful in practice, since real attackers can embed a trigger as an added pattern, a swapped-in patch, or a blended overlay. By deliberately varying both the *type* of pattern (additive, patch, or blend) and the *scope* of the attack (whether it corrupts one source class or many), these settings stress-test whether UnivBD's detection statistic genuinely generalizes across the backdoor attack landscape, rather than just memorizing the signature of one attack family.

## Mechanics {#mechanics}
Three common backdoor pattern (BP) types are considered: additive perturbation, patch replacement, and blending. Concretely, five specific BP instances are used — a global chessboard pattern and a local pixel perturbation for additive perturbation, a noisy patch and a unicolor patch for patch replacement, and a blended noisy patch for blending — collectively labeled A1 through A5 [§sec_4_1_1].

For A2 the perturbed pixel is randomly chosen and then fixed per attack, while for A3–A5 both the patch color and its location are randomly chosen and fixed per attack, giving each generated backdoor attack (BA) a unique but reproducible trigger [§sec_4_1_1].

Each BA is constrained to a single target class, randomly selected per attack, but the source classes may be single ("S") or multiple ("M"): under "S" one source class is randomly chosen, while under "M" ten source classes are sampled for TinyImageNet and all non-target classes are used for the other three datasets. Combining a BP label with a source-class setting yields compact attack identifiers such as "A1-M" (chessboard pattern, multiple source classes) [§sec_4_1_1].

Dataset-specific ensembles are built from these settings: CIFAR-10 uses all ten combinations of A1–A5 with S/M, CIFAR-100 and GTSRB use five ensembles (A1–A5) under "M" only, and TinyImageNet uses a single "A3-M" ensemble due to its training cost; ten independently generated BAs make up each ensemble, alongside a matching ensemble of ten clean classifiers per dataset to measure false detection rate [§sec_4_1_1].

## The Math {#the-math}
The local context describes categorical experimental settings (BP types, source-class modes, dataset ensembles) rather than any formal statistic or equation, so there is no equation to reproduce for this concept [§sec_4_1_1].

## Go Deeper {#go-deeper}
No research note is attached to this concept, so no external resources are available to cite here. For related material within this wiki, see the parent concept UnivBD (Universal Backdoor Detector) and the individual pattern types this concept composes: Additive Perturbation BP, Patch Replacement BP, and Blending BP.
