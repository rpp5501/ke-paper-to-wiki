# English Constituency Parsing

## TL;DR {#tldr}
English constituency parsing is one of two out-of-domain generalization tests for the Transformer (the other being translation), and the surprising result — a purely attention-based sequence model producing state-of-the-art parse trees with almost no task-specific tuning — is offered as evidence that Transformer works as a general-purpose architecture, not just a translation trick.

## Intuition {#intuition}
Constituency parsing means outputting a full syntactic tree for a sentence, and it's a much harder sequence-to-sequence target than translation: the output is long relative to the input, it must obey strict structural constraints (a well-formed tree), and, historically, generic recurrent sequence-to-sequence models had struggled to be competitive here, especially without huge amounts of training data. Testing the Transformer on this task is a way of asking "does this architecture actually understand structure, or did it just get lucky on translation?" Success here strengthens the paper's core claim about the Transformer, described elsewhere as a general building block.

## Mechanics {#mechanics}
The model used is a 4-layer Transformer, notably smaller than the translation models described elsewhere in the paper, trained directly on parse trees as a sequence-to-sequence task [§sec_6_3]. It was trained in two regimes: WSJ-only, using about 40K labeled sentences from the Penn Treebank, and semi-supervised, using roughly 17M sentences drawn from larger high-confidence and BerkeleyParser corpora [§sec_6_3]. Vocabulary size was adapted to the setting — 16K tokens for WSJ-only, 32K tokens for semi-supervised — reflecting the larger and noisier data in the semi-supervised case [§sec_6_3].

Critically, almost all hyperparameters were carried over unchanged from the base English-to-German translation model; the authors only tuned dropout (both attention and residual), learning rate, and beam size, using the Section 22 development set [§sec_6_3]. This minimal-tuning setup is itself part of the experimental point: strong results without task-specific architecture changes suggest the Transformer generalizes rather than overfitting to translation-specific tricks. At inference time, the maximum output length was extended relative to input length to accommodate the verbosity of tree notation, and beam search was used for both training regimes [§sec_6_3].

## The Math {#the-math}
The local context provides no equations specific to parsing — the task reuses the Transformer's standard sequence-to-sequence formulation (encoder-decoder attention producing an output sequence, here a linearized parse tree) rather than introducing new mathematical machinery [§sec_6_3].

## Go Deeper {#go-deeper}
- Table in §sec_6_3 — compares WSJ F1 scores across discriminative, semi-supervised, multi-task, and generative parsers (Petrov et al. 2006; Zhu et al. 2013; Dyer et al. 2016; Vinyals & Kaiser et al. 2014; Luong et al. 2015), useful for seeing exactly where the Transformer (91.3 WSJ-only, 92.7 semi-supervised) lands relative to prior state of the art, including the one model it didn't beat (the Recurrent Neural Network Grammar, generative, 93.3).
- No dedicated research note exists for this concept — the section text above is the only available local material.
