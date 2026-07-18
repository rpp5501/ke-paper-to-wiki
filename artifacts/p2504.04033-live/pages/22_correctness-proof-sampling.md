# Correctness Proof of Sampling Technique

## TL;DR {#tldr}
This concept proves that the sampling procedure used to build the attacker's auxiliary dataset actually delivers the target correlation between the sensitive attribute and the output that the Single Attribute-based Targeted Attack relies on. Rather than assuming the constructed sample "just works," the proof derives closed-form counts for how many records of each type must be drawn so the resulting Pearson correlation matches the desired value. Because record counts must be whole numbers, the proof also explains why the achieved correlation is only an extremely close approximation of the target rather than an exact match.

## Intuition {#intuition}
Think of the attacker choosing how many records fall into each of four buckets defined by whether the sensitive attribute and the output are "positive" or "negative." If the attacker wants a specific correlation strength between the two variables, and also wants the sample split evenly between positive and negative sensitive-attribute values, then the bucket sizes aren't free choices — they're pinned down by algebra once the target correlation and split ratio are fixed. The catch is that bucket sizes must be integers, so the attacker rounds the derived values down or up, which nudges the realized correlation slightly away from the exact target. The proof's payoff is showing that this nudge is negligible, so the sampled dataset is a trustworthy stand-in for one with the exact desired correlation.

## Mechanics {#mechanics}
The setup lets the sensitive attribute and the output each be treated as binary-valued variables over a total of records, with the correlation between them defined by the standard Pearson formula relating sums and cross-products of the two variables [§sec_11_1]. Because each variable takes only two values, the aggregate sums appearing in that formula collapse into counts of records falling into each of the four combinations of sensitive-attribute value and output value, which lets the correlation be rewritten purely in terms of these four counts [§sec_11_1]. The attacker's design requirement — an equal number of positive and negative output samples, together with a fixed ratio between positive and negative sensitive-attribute samples — imposes two additional linear constraints on these same four counts [§sec_11_1]. Substituting the design constraints into the rewritten correlation expression reduces the problem to a system that can be solved directly for the counts, first recovering the row/column totals and then the individual cell counts of the four-way breakdown [§sec_11_1]. Since these counts must be integers, the solved values are rounded using floor and ceiling operations, meaning the sampled records realize a correlation only approximately equal to the target, with a difference the proof characterizes as negligible for the attack's purposes [§sec_11_1].

## The Math {#the-math}
The starting point is the standard Pearson correlation coefficient between the sensitive attribute and output over records [eq_4].
$$
c = \frac{n\sum sy - (\sum s)(\sum y)}{\sqrt{\left( n\sum s^2 - n (\sum s)^2\right)\left( n\sum y^2 - n (\sum y)^2\right)}}
$$ [eq_4]

Because and are binary, this expression can be rewritten in terms of the four joint-count variables counting records with each combination of sensitive-attribute and output sign [eq_5].
$$
c = \frac{n_+^+ \times n_-^- - n_+^- \times n_-^+}{\sqrt{(n_+^+ + n_+^-)(n_+^+ + n_-^+)(n_-^+ + n_-^-)(n_+^- + n_-^-)}}
$$ [eq_5]

The attacker's sampling requirements — an even positive/negative output split and a fixed sensitive-attribute ratio of — impose the following constraints on the row and column totals of those four counts [eq_6].
$$
n_+^+ + n_-^+ = n_+^- + n_-^- = \frac{n}{2} \\
    n_+^+ + n_+^- = \frac{n}{m+1}, \quad n_-^+ + n_-^- = \frac{mn}{m+1}
$$ [eq_6]

Substituting these totals back into the correlation expression yields a simplified relation between the cross-count difference and the target correlation [eq_7].
$$
n_+^+ \times n_-^- - n_+^- \times n_-^+ = c \sqrt{m} \times \frac{n}{m+1} \times \frac{n}{2}
$$ [eq_7]

Combining this with the row/column totals isolates the difference between two of the four counts, giving a directly solvable equation for the remaining unknowns [eq_8].
$$
n_-^- - n_-^+ = c \sqrt{m} \times \frac{n}{m+1}
$$ [eq_8]

Solving [eq_6] and [eq_8] together gives the row/column totals and , which are then substituted back to obtain and , after which floor/ceiling rounding is applied since all four counts must be integers [§sec_11_1].

## Go Deeper {#go-deeper}
No research note is attached to this concept, so there are no external resources to list here.
