# Attention Visualizations

## TL;DR {#tldr}
Attention visualizations are diagnostic plots that show, for a given word, how strongly each attention head attends to every other word in the sequence. They provide qualitative evidence that Multi-Head Attention learns interpretable structure — such as long-distance syntactic dependencies and coreference — rather than acting as an opaque black box.

## Intuition {#intuition}
Because each attention head produces a distribution of weights over all positions in a sentence, that distribution can be drawn directly as colored lines or highlights connecting a query word to the words it "looks at." Different heads, shown in different colors, often specialize: one head might consistently jump across a long clause to link a verb with its dependent phrase, while another head sharpens its focus on pronouns to resolve what they refer to. This turns the abstract claim that attention "learns relationships" into something that can be inspected by eye, head by head.

## Mechanics {#mechanics}
One visualization example examines encoder self-attention at layer 5 of 6, focusing on attentions from the word "making." Many attention heads are shown attending to a distant dependency of "making," completing the phrase "making...more difficult" — demonstrating that the model captures long-distance dependencies rather than only local, nearby-word relationships [§sec_8].

A second example, also from layer 5 of 6, isolates two attention heads (heads 5 and 6) whose behavior appears related to anaphora resolution. The figure contrasts the full attention pattern of head 5 with the isolated attentions from just the word "its" for heads 5 and 6, noting that these attentions are very sharp for that word — i.e., concentrated on a small number of positions rather than spread diffusely [§sec_8].

Across both examples, the broader observation is that many attention heads exhibit behavior tied to the syntactic and semantic structure of the sentence, and that different heads from the same encoder self-attention layer clearly learn to perform different tasks [§sec_8].

## The Math {#the-math}
The local context for this concept describes qualitative visualization examples and contains no equations; the underlying attention-weight computation these visualizations plot belongs to the Multi-Head Attention concept rather than to this note. [§sec_8]

## Go Deeper {#go-deeper}
- No research note is available for this concept — the local context above (Section sec_8, the paper's attention visualization figures) is the only source material provided.
