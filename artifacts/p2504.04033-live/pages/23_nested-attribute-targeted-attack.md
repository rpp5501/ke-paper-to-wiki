# Nested Attribute-based Targeted Attack

## TL;DR {#tldr}

The Nested Attribute-based Targeted Attack is the most powerful (L3) member of the Targeted Attribute Inference Attack family. Where the Single Attribute-based Targeted Attack narrows the victim pool using one sensitive attribute, this attack combines several attributes at once, intersecting their most vulnerable subgroups to zero in on an even smaller, higher-risk set of records.

## Intuition {#intuition}

Think of the single-attribute attack as filtering a population by one property — say, occupation — and keeping only the riskiest occupational groups. The nested attack repeats this filtering across several attributes and stacks the filters on top of each other, keeping only records that fall in the risky segment for every attribute considered. Because each additional filter narrows the pool further, the resulting nested groups are smaller but disproportionately concentrated with the most privacy-vulnerable individuals — much like combining several loosely correlated risk factors to find the population segment where risk compounds.

## Mechanics {#mechanics}

The attack begins by choosing how many attributes to nest together, then reuses the first three steps of the single attribute-based targeted attack, applied independently to each candidate attribute, to compute the range of angular differences for that attribute's groups; only the top attributes by this range are kept for nesting [§sec_5_3_2].

For each selected attribute, records are partitioned into groups by that attribute's values, and the groups are ranked by their angular difference so that the most vulnerable ones can be identified [§sec_5_3_2].

From this ranking, an "above-average-risk segment" is built per attribute by taking the top-ranked groups whose combined size approaches half of all records covered by that attribute, and the indices identifying these groups are recorded as the risk segment for the attribute [§sec_5_3_2].

The core nesting step then intersects the above-average-risk segments across the chosen attributes, forming nested groups from the overlap of each attribute's risky subset rather than considering every possible combination of groups, which keeps the search tractable [§sec_5_3_2].

Because evaluating every combination of nested groups across attributes is exponentially expensive, the method is deliberately greedy: it fixes the number of attributes considered to the attack budget and processes attributes in order of their angular-difference ranking rather than searching the full combinatorial space [§sec_5_3_2].

When the attack budget is too small to include the full above-average-risk segment of the last attribute added, the attack selects as many of that attribute's risky groups as the remaining budget allows while still satisfying the risk condition, and outputs the nested configuration with the lowest budget usage that meets this condition [§sec_5_3_2].

## The Math {#the-math}

The local context describes the selection and intersection procedure in prose — defining ordered index sets, top-k group selections, and above-average-risk segments per attribute — but does not provide a numbered display equation for this concept, so no [eq_N] block can be reproduced here [§sec_5_3_2].

## Go Deeper {#go-deeper}

No research note is attached to this concept, so there are no external resources to list here.
