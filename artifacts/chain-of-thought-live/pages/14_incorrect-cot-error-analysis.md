# Incorrect Chain of Thought Analysis

## TL;DR {#tldr}

The authors hand-checked 50 wrong GSM8K answers from the 137B model and sorted them by what would need to change to fix the reasoning, not by surface symptom. Most errors are shallow — a calculator slip, a wrong number symbol, one missing step — but just over half require a real rewrite, usually because the model misunderstood the problem.

## Intuition {#intuition}

A wrong final answer hides very different failure modes: sometimes the model reasoned perfectly and only fumbled the arithmetic, sometimes it reasoned about the wrong thing entirely. Building on the raw accuracy numbers from arithmetic reasoning results, this analysis asks a sharper question than "how often is it wrong" — it asks "how far is wrong from right," which points directly at what kind of fix (a calculator, better prompting, better world knowledge) would actually help.

## Mechanics {#mechanics}

The authors manually inspected 50 GSM8K outputs the 137B model got wrong, choosing an error taxonomy based on what edit would make the chain of thought correct rather than what surface feature it exhibits [§sec_14_2].

| Category | Count | Share | Note |
|---|---|---|---|
| Calculator error only | 8/50 | 16% | Chain of thought fully correct except for the arithmetic; an external calculator would fix it entirely [§sec_14_2] |
| Symbol mapping error | 8/50 | 16% | Reasoning is correct, only the number symbols in the equations are wrong; fixable by editing equations alone, not the words [§sec_14_2] |
| One step missing | 11/50 | 22% | Correct except that a single reasoning step was omitted [§sec_14_2] |
| Substantial edit needed | 27/50 | 54% | Requires major rewriting, almost always involving a semantic-understanding error [§sec_14_2] |

Calculator errors cut across categories: 34 of the 50 examples contained an arithmetic slip in addition to some other issue, so the "calculator error only" row above counts just the cases where a calculator fix was the entire remedy [§sec_14_2].

| Condition | GSM8K solve rate (137B) |
|---|---|
| Chain-of-thought prompting alone | 14.3% [§sec_14_2] |
| Chain-of-thought + external Python calculator | 17.3% [§sec_14_2] |

Beyond the four headline categories, 8 of the 27 substantial-edit cases were also incoherent: some sentence in the generated chain did not follow from what came before it or contradicted basic world knowledge [§sec_14_2].

Because a wrong reasoning process can still land on the right final answer by chance, the paper flags free-response tasks as more trustworthy diagnostics than binary-classification tasks, where an incoherent chain has a much higher chance of getting graded correct anyway [§sec_14_2].

## The Math {#the-math}

Adding a Python calculator moved the 137B solve rate on GSM8K from 14.3% to 17.3%, a gain of 3.0 percentage points, or a 21% relative improvement (17.3/14.3 ≈ 1.21) [§sec_14_2].

The four category counts (8, 8, 11, 27) sum to 54 against a sample of 50, and their percentages (16%, 16%, 22%, 54%) sum to 108% rather than 100% [§sec_14_2].

The paper attributes part of this to overlap: 34 of the 50 examples carried a calculator slip alongside another flaw, so calculator errors cut across the other categories instead of forming a disjoint fifth bucket [§sec_14_2].

If a perfect calculator fixed every calculator-only error, the ceiling would be higher than what was observed: 16% of the 85.7% error rate (100% − 14.3%) is 13.7 points, implying accuracy near 28%, but the actual gain from adding a Python calculator was only 3.0 points (14.3% → 17.3%) [§sec_14_2].

That roughly 4.5× gap between the potential (~13.7 points) and the actual (3.0 points) suggests the automated calculator does not fully substitute for the manual fix: many of the 34 combined-error examples needed the correct equation set before the calculator could help, so the calculator alone left other errors in place [§sec_14_2].

## Go Deeper {#go-deeper}

- The 54% "substantial edit" bucket is dominated by semantic-understanding failures, tying this analysis to the open problem of grounding language-model generations in context and world knowledge [§sec_14_2].
- One proposed fix is decoding multiple reasoning paths and scoring them with a learned verifier, though the paper notes this requires training the verifier separately — an added cost the calculator-only fix does not incur [§sec_14_2].
