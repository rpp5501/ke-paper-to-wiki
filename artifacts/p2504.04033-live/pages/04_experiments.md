# Experiments
## TL;DR {#tldr}
This section is the empirical backbone of the paper's disparate privacy vulnerability argument: it lays out how the authors test their targeted attribute inference attacks against real datasets and models, then reports how those attacks perform. It ties together the experimental setup, the comparison between ideal and practical imputation attacks, disparity-focused inference results, and overall targeted attribute inference performance, all building on the attack methodology defined earlier in the paper.

## Intuition {#intuition}
Rather than just proposing attacks in the abstract, the authors want to show they actually work — and, more importantly, that they work *unevenly* across different groups or individuals, which is the core "disparate vulnerability" claim of the paper. Think of this section as the proving ground: it sets up datasets and models, then runs the attacks to see who gets exposed and by how much, connecting the theoretical attack methodology to concrete, measurable outcomes.

## Mechanics {#mechanics}
The section is organized as an experimental narrative: first establishing the experimental arrangement, datasets, machine learning models, and performance metrics used throughout, and then examining how the proposed attacks perform under those conditions [§sec_6]. This structure means the section functions as an umbrella for several sub-analyses — the setup, the ideal-versus-practical imputation comparison, disparity inference performance, and targeted attribute inference performance — each of which elaborates on a piece of this overall arrangement [§sec_6].

## The Math {#the-math}
The local context for this section provides only a high-level description of the experimental section's scope and does not include any equations, so no formulas can be reproduced here [§sec_6].

## Go Deeper {#go-deeper}
No research note is available for this concept, so there are no additional resources to list beyond the paper's own subsections — see Experimental Setup, Ideal vs. Practical Imputation Attacks, Disparity Inference Attack Performance, and Targeted Attribute Inference Attack Performance for the detailed breakdowns this section summarizes.
