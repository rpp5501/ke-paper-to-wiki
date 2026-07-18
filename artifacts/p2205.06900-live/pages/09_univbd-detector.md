# UnivBD (Universal Backdoor Detector)
## TL;DR {#tldr}
UnivBD is the post-training backdoor detector introduced by the MM-BD paper, built on the paper's Detection Procedure and evaluated in the Experiments section against a range of backdoor pattern (BP) types. It is designed to work regardless of the specific pattern type used to poison a model, which is what distinguishes it from baseline detectors such as NC and TABOR that are typically tuned to narrower classes of triggers.

## Intuition {#intuition}
The core idea behind UnivBD is generality: rather than searching for a specific kind of trigger (e.g., a small patch in a fixed location), it is meant to catch backdoors regardless of how the attacker's pattern looks or where it appears. This positions it as a "universal" counterpart to earlier detectors, which tend to assume a particular backdoor pattern type and can be blind to attacks outside that assumption. The Experiments section exists precisely to stress-test this generality claim by throwing many different BP types and source-class configurations at the detector and comparing its performance to established baselines.

## Mechanics {#mechanics}
The main experiments evaluate UnivBD's detection accuracy and efficiency against several state-of-the-art post-training backdoor detectors across a variety of backdoor attack (BA) configurations, including different BP types and numbers of source classes [§sec_4_1]. The BP types tested span a deliberately diverse set of trigger visuals — a chessboard pattern (A1), a single pixel (A2), a noisy patch (A3), a unicolor patch (A4), and a blended patch (A2 variant) — illustrated both as standalone patterns and as they appear once embedded into images [§sec_4_1]. This breadth of BP types is the mechanism by which the experiments substantiate UnivBD's "universal" label: performance is measured not on one attack style but across this whole settings grid before being compared to baseline detectors [§sec_4_1].

## The Math {#the-math}
The local context for this section describes the experimental setup and BP type gallery but does not include any equations for UnivBD's detection statistic itself [§sec_4_1].

## Go Deeper {#go-deeper}
No research note is available for this concept, so there are no additional resources to list here.
