# Next steps — generated 2026-08-04

## Identifiability-aware SID for latent confounders
Extend the SID to explicitly exclude or flag node pairs whose intervention distributions are non-identifiable under hidden variables, mirroring the CPDAG exclusion strategy. This would make the distance usable on causally insufficient systems, a common real-world setting.
anchors: nodes=['hidden-variables-extension'] sources=['§sec_2_4_6']

## Joint/multi-node intervention distance
Generalize the pairwise SID lemma to sets of simultaneously intervened nodes, handling the combinatorial union-of-parents adjustment needed for correctness. This would let the metric evaluate graph quality for policies that intervene on multiple variables at once.
anchors: nodes=['multiple-interventions-extension'] sources=['§sec_2_4_7']

## Vector-valued or multi-facet successor to scalar SID
Since a single scalar SID collapses distinct error modes (identifiability failures, multi-intervention effects) into one number, design a multi-component distance that reports these facets separately rather than averaging them away. This directly builds on the hidden-variable and multi-intervention extensions as the component axes of the new metric.
anchors: nodes=['hidden-variables-extension', 'multiple-interventions-extension'] sources=['§sec_5', '§sec_2_4_6', '§sec_2_4_7']
