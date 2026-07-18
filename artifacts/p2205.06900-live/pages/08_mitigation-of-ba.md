# Mitigation of Backdoor Attack

## TL;DR {#tldr}
Once MM-BD's Detection Procedure flags a classifier as backdoored, the victim network doesn't have to be thrown away. Instead of always swapping in a new model from a trusted source, MM-BD offers a repair path: it caps the activation of every neuron in every layer at a tightly optimized upper bound, choking off the abnormally large activations that the backdoor relies on, while leaving accuracy on clean inputs essentially untouched.

## Intuition {#intuition}
A backdoor works by hijacking a subset of neurons and driving their activations to unusually large values whenever the trigger pattern is present; this surge propagates layer by layer until it dominates the logit for the attacker's target class — exactly the signal the Maximum-Margin statistic exploits for detection. The mitigation idea is to attack the same weakness from the defender's side: clamp every neuron's activation to the smallest ceiling that still lets the network classify clean, legitimate samples correctly. A benign neuron rarely needs to fire that hard anyway, so clean accuracy survives; a backdoored neuron, however, is starved of the extreme activation it needs to force a misclassification.

## Mechanics {#mechanics}
If the attack is detected, one option is simply to discard the victim classifier and obtain a new one from a trustworthy training authority, or to keep using the existing classifier for all classes other than the identified BA target class; mitigation is offered as an alternative to these choices [§sec_3_3]. The approach is motivated by the same phenomenon underlying detection: a BA induces a subset of neurons in each layer to reach abnormally large activation, an effect that accumulates layer by layer into a large maximum margin for the BA target class [§sec_3_3]. A related detection technique exploits this same large-activation phenomenon but needs several hyperparameters, such as a procedure to select which neurons are responsible for the excess activation; the mitigation method here instead applies a specifically optimized upper bound to every neuron, with no selection step, to suppress any possible large activation caused by the backdoor without significantly degrading accuracy on clean samples [§sec_3_3]. For each layer, a bounding vector is introduced so that the layer's activation function is replaced by a bounded version, clipping each neuron's output at its own optimized ceiling [§sec_3_3]. The bounding vectors are chosen by solving an optimization problem: minimize the norm of the bounding vectors (i.e., clamp activations as tightly as possible) subject to the constraint that classification accuracy on a small set of clean, correctly-classified legitimate samples stays at or above a minimum accuracy benchmark [§sec_3_3]. To solve this in practice, the constrained problem is converted into a Lagrangian minimized via gradient descent, with the penalty multiplier initialized large and then updated automatically so the accuracy constraint is met [§sec_3_3]. The first term of the Lagrangian keeps the classifier's logits on the clean samples in the mitigation set close to their original, unbounded values; this both helps satisfy the accuracy constraint and prevents the logit of each sample's true class from being further inflated (avoiding overfitting), which is what allows mitigation to succeed even with a limited number of clean samples [§sec_3_3]. The final mitigated classifier is obtained by applying a softmax to the logits computed with the optimized bounding vectors [§sec_3_3].

## The Math {#the-math}
The unmodified logit for class $c$ on input $\mathbf{x}$ is written as a linear readout of the last hidden layer's activation, composed through all $L$ layers of the network [eq_4]:

$$
g_c({\bf x}) = {\bf w}^T_c (\sigma_L \circ \cdots \circ \sigma_1 ({\bf x}))+b_c,
$$ [eq_4]

Introducing a bounding vector $\mathbf{z}_l$ at every layer $l \ge 2$ replaces each activation function with its bounded counterpart, giving a bounded logit that depends on the full set of bounding vectors $\mathbf{Z}$ [eq_5]:

$$
\bar{g}_c({\bf x}; {\bf Z}) = {\bf w}^T_c ( \bar{\sigma}_L ( \bar{\sigma}_{L-1} ( \cdots \bar{\sigma}_2( \sigma_1 ({\bf x}) ;{\bf z}_2) \cdots ;{\bf z}_{L-1}) ;{\bf z}_L) )+b_c,
$$ [eq_5]

Finding the bounding vectors reduces to minimizing their total norm subject to an accuracy constraint on the clean mitigation set $\mathcal{D}$, with $\pi$ the minimum accuracy benchmark [eq_6]:

$$
\begin{aligned}
	& \underset{{\bf Z}=\{{\bf z}_2, \cdots, {\bf z}_L\}}{\text{min}}
	& & \sum_{l=2}^L ||{\bf z}_l||_2 \\
	& \text{subject to}
	& & \frac{1}{|{\mathcal D}|}\sum_{({\bf x}, y)\in{\mathcal D}}{\mathds 1}[y=\argmax_{c\in{\mathcal Y}} \bar{g}_c({\bf x}; {\bf Z})] \geq \pi,
\end{aligned}
$$ [eq_6]

This constrained problem is solved in practice by gradient descent on its Lagrangian relaxation, where the squared logit-discrepancy term keeps bounded and unbounded logits close on $\mathcal{D}$ and $\lambda$ is driven to enforce the accuracy constraint [eq_7]:

$$
L({\bf Z}, \lambda; {\mathcal D}) = -\frac{1}{|{\mathcal D}|\times|{\mathcal Y}|} \sum_{({\bf x}, y)\in{\mathcal D}} \sum_{c\in{\mathcal Y}} [\bar{g}_c({\bf x}; {\bf Z}) - g_c({\bf x}; {\bf Z})]^2 + \lambda \sum_{l=2}^L ||{\bf z}_l||_2,
$$ [eq_7]

## Go Deeper {#go-deeper}
No research note is attached to this concept. For the broader system this mitigation step plugs into, see the parent page **MM-BD: Maximum-Margin Backdoor Detection**; for the trigger condition that precedes mitigation, see **Detection Procedure**, which this concept builds on; and for the concrete step-by-step procedure implementing the optimization sketched above, see **Algorithm for BA Mitigation**.
