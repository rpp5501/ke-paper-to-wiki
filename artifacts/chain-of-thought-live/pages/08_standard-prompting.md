# Standard Prompting
## TL;DR {#tldr}

Standard prompting is the few-shot baseline this paper defines chain-of-thought prompting against: exemplars pair an input directly with a final answer, with no intermediate reasoning steps shown or elicited [§sec_2].

## Intuition {#intuition}

Picture a student who, when asked to solve a word problem, writes only the final number on the answer line and skips the scratch work entirely. That is standard prompting: the model sees a handful of examples that go straight from question to answer, so it learns to produce answers the same way, in one leap.

Chain-of-thought prompting is the same student showing every step of arithmetic before circling the final number. The paper positions standard prompting as this stripped-down baseline, useful for measuring how much showing the work actually buys a model on hard reasoning problems.

## Mechanics {#mechanics}

People solve a multi-step math word problem by decomposing it into intermediate steps, solving each one, and only then giving the final answer [§sec_2].

Standard prompting skips that decomposition: its few-shot exemplars run from question straight to answer, so the behavior being demonstrated is a direct question-to-answer mapping rather than a solution path [§sec_2].

Chain-of-thought prompting instead lets the model emit intermediate reasoning steps before its final answer, mirroring that human decomposition process [§sec_2].

Standard prompting is defined in the paper only by contrast: it is whatever exemplar format remains once those intermediate steps are removed, leaving just input and output [§sec_2].

Standard prompting's counterpart in this paper's neighborhood is chain-of-thought prompting, the concept the paper actually develops and evaluates [§sec_2].

The paper never gives standard prompting its own defining passage; every property attributed to it here is inferred by negating a property claimed for chain-of-thought prompting [§sec_2].

The paper lists four advantages of showing intermediate steps, and each one names something standard prompting forgoes by not showing them:

- **Decomposition:** intermediate steps let the model allocate more computation to problems that need more reasoning steps; standard prompting spends the same fixed computation on every question regardless of difficulty [§sec_2].
- **Interpretability:** intermediate steps give a debuggable window into how the model reached an answer; standard prompting exposes only the final answer, with no path to inspect [§sec_2].
- **Generality:** intermediate steps apply, at least in principle, to any task a human could solve via language, including arithmetic, commonsense, and symbolic reasoning; standard prompting is not credited with this same reach [§sec_2].
- **Elicitation:** intermediate steps can be elicited from sufficiently large off-the-shelf models simply by adding chain-of-thought exemplars; standard prompting exemplars carry no such reasoning demonstration to elicit [§sec_2].

| Dimension | Standard prompting | Chain-of-thought prompting |
|---|---|---|
| Exemplar format | question → answer pairs, no intermediate content [§sec_2] | question → intermediate reasoning steps → answer [§sec_2] |
| Computation per problem | fixed, independent of how many steps the problem needs [§sec_2] | scales with the number of intermediate steps generated [§sec_2] |
| Interpretability | none — the answer is opaque [§sec_2] | intermediate steps expose how the answer was reached, though not a full account of the model's computation [§sec_2] |

## The Math {#the-math}

Sec_2 supplies no display equation for standard prompting, but its own language points to a quantitative argument about computation budget worth making explicit [§sec_2].

Take a word problem that needs three chained arithmetic operations before the final number is correct. Standard prompting's exemplars show the model only the pair (question, final number), so nothing in the demonstration reserves extra output tokens for the three intermediate operations — the model is trained by example to jump directly to a number for any question, easy or hard [§sec_2].

Chain-of-thought prompting's exemplars instead show (question, step 1, step 2, step 3, final number), so the amount of generated text — and thus the amount of computation spent — grows with the number of steps the problem actually requires [§sec_2].

This gives a boundary case: on a one-step problem, the two formats converge, since there is only one thing to compute and standard prompting's single leap covers it [§sec_2]. As the required step count grows, standard prompting still spends one fixed leap while chain-of-thought prompting's budget grows with it, which is exactly the "additional computation... allocated to problems that require more reasoning steps" that sec_2 credits to chain-of-thought and withholds from its standard counterpart [§sec_2].

## Go Deeper {#go-deeper}

The paper is explicit that chain-of-thought's interpretability is partial: intermediate steps suggest how an answer might have been reached, but "fully characterizing a model's computations that support an answer remains an open question" [§sec_2] — a caveat that applies with even less to offer under standard prompting, since it has no intermediate trace to inspect at all.

For the full mechanics of the contrasting method, see the Chain-of-Thought Prompting concept page, which this page's neighborhood links to directly.
