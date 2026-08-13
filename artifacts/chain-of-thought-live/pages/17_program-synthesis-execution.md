# Program Synthesis and Execution

## TL;DR {#tldr}
Prior work reasons by having a model write and then execute a program — code is the intermediate step. Chain-of-thought keeps the idea of intermediate steps but drops the requirement that they be executable code, making the technique open-domain rather than domain-specific.

## Intuition {#intuition}
Executing a program is reasoning through a fixed, mechanical procedure. Once you commit to "write code that adds two numbers," every subsequent step is forced by the semantics of addition — carry the 1, move to the next digit, repeat.

Chain-of-thought keeps the same idea of decomposing a hard problem into intermediate steps, but drops the requirement that a step be executable code. A step can be "the elephants are twice the number of monkeys" as easily as a line of Python.

## Mechanics {#mechanics}
Using intermediate reasoning steps has a long history in program synthesis and execution, a line of prior work that splits into two strands: architectural innovations built specifically for the task, and the more recent use of large language models to synthesize or execute programs [§sec_13_3].

The program execution work closest to this paper shows that large language models can perform up to 10-digit addition, evaluate polynomials, and execute python programs [§sec_13_3].

Generating a program and then executing it can itself be viewed as a type of reasoning, but it stays tied to whatever domain the program targets — arithmetic, polynomials, code [§sec_13_3].

Chain-of-thought generalizes those domain-specific primitives to natural language, which is open-domain and applies in principle to any text-to-text NLP task [§sec_13_3].

| Dimension | Program synthesis & execution (prior work) | Chain-of-thought prompting |
|---|---|---|
| Representation of a step | Executable code or a formal expression (e.g. a line of Python, a polynomial term) | A natural-language sentence, unconstrained by formal syntax [§sec_13_3] |
| Domain coverage | Domain-specific: arithmetic, polynomial evaluation, Python execution | Open-domain: applies in principle to any text-to-text NLP task [§sec_13_3] |

## The Math {#the-math}
**A 10-digit addition as a fixed execution trace:** the cited result is that language models can perform up to 10-digit addition [§sec_13_3]. Adding two such numbers, e.g. 4,827,193,650 + 3,956,081,247, takes exactly 10 sequential carry-propagation steps — one per digit position, each conditioned only on the current digit pair and the carry bit from the previous step [§sec_13_3].

That step count is fixed by the input's digit length, not by the difficulty of the underlying claim — every 10-digit addition takes 10 steps, whether the digits are trivial or not [§sec_13_3].

**Why "up to 10-digit" marks a tested ceiling, not a proven limit:** the evidence reports a demonstrated capability, not a scaling law relating error rate to digit count [§sec_13_3]. Nothing in the citation states that an 11-digit addition is impossible — only that 10 digits is where this evaluation stopped [§sec_13_3].

Chain-of-thought's steps are not fixed to a single formal grammar the way a carry-propagation trace is; the same decomposition applies whether the task is arithmetic, commonsense, or symbolic, because the step is natural language rather than a domain-specific primitive [§sec_13_3].

## Go Deeper {#go-deeper}
This concept sits in the paper's Related Work under "Prompting," positioned against the program-synthesis lineage its own approach diverges from. For the mechanism chain-of-thought substitutes in place of code execution, see the concept covering chain-of-thought prompting itself.
