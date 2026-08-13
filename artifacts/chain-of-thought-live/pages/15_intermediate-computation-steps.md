# Intermediate Language Steps

## TL;DR {#tldr}

CoT prompting is not the first method to give a model intermediate steps — finetuning-based methods already demonstrated broad benefits from this idea [§sec_13_5].

What's new is eliciting the same behavior from a frozen, off-the-shelf model through prompting alone, with no labeled training set and no gradient update [§sec_13_5].

## Intuition {#intuition}

Two ways exist to teach a model to show its work. One trains the ability in, adjusting weights on examples of intermediate steps. The other asks for it, describing the steps you want in the prompt and leaving the weights untouched [§sec_13_5].

Prior work already showed the trained-in version works: it improves performance, robustness, training speed, and more [§sec_13_5]. The prompted version described here gets the same ability from a model that was never shown a single labeled reasoning trace [§sec_13_5].

## Mechanics {#mechanics}

Prior work already established that giving a network the ability to produce intermediate steps confers benefits across many settings [§sec_13_5]. The reported benefits span:

- Improved task performance [§sec_13_5]
- Improved robustness [§sec_13_5]
- Faster training [§sec_13_5]
- Reduced bias [§sec_13_5]
- Extension to image and reinforcement-learning settings [§sec_13_5]

To grant this ability, prior work typically finetunes a model on a training set of intermediate steps, either hand-annotated or synthetically generated [§sec_13_5].

The prompting route reaches these same abilities without a finetuning step [§sec_13_5]. A single frozen model handles many reasoning tasks, since the intermediate steps come from the prompt's exemplars rather than from a weight update [§sec_13_5].

This setup matters for two practical reasons [§sec_13_5]:

- Removes the need for a large labeled annotation set [§sec_13_5]
- Lets one model cover a range of reasoning tasks with zero gradient updates [§sec_13_5]

## The Math {#the-math}

Treat the finetuning route as a cost that grows with T, the number of reasoning tasks a model must support [§sec_13_5]. Each task requires its own labeled or synthetic training set of intermediate steps, plus its own finetuning run over the full parameter set [§sec_13_5].

That puts the annotation cost and the update cost both at O(T): T datasets to build, T finetuning runs to execute, one per task [§sec_13_5].

The prompting route changes the shape of that cost. The frozen parameters are shared across every task, so the O(T) finetuning-run term drops to zero regardless of how many tasks the model is asked to handle [§sec_13_5].

The boundary case is a single task, T = 1 [§sec_13_5]. Finetuning's update cost then drops to one run, converging with prompting's zero-update cost [§sec_13_5].

The annotation-cost gap still remains at T = 1: finetuning needs a full training set for that task, while prompting needs only the exemplars written directly into the prompt [§sec_13_5].

## Go Deeper {#go-deeper}

The supplied evidence names the categories of prior benefit — performance, robustness, training speed, bias, image and RL — but strips the specific citations behind each claim [§sec_13_5].

It also leaves open whether prompting reaches the same ceiling that finetuning reaches on any of these benefits, or only recovers the ability without matching its strength [§sec_13_5].
