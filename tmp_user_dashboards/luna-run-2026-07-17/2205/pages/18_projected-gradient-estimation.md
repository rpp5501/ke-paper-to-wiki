# Projected Gradient Estimation

## TL;DR {#tldr}
MM-BD approximates each maximum margin with gradient ascent from multiple random initializations, projecting every iterate back into the valid input set.

## Intuition {#intuition}
Finding the highest hill in a complicated landscape depends on where you start. Multiple starts give the search several chances, while projection keeps the synthetic probe inside the image domain rather than letting it become an invalid input.

## Mechanics {#mechanics}
For each class, the method runs gradient ascent on the margin objective, uses a convergence criterion, and takes the largest local optimum from 30 random initializations in the main experiments [§sec_1]. Projection is appropriate for domains such as pixel boxes, where valid inputs form a closed convex set [§sec_1].

## The Math {#the-math}
A projected update can be written schematically as $$\mathbf{x}^{(s+1)}=\Pi_{\mathcal{X}}\left(\mathbf{x}^{(s)}+\eta\nabla_{\mathbf{x}}m_c(\mathbf{x}^{(s)})\right)$$ [§sec_1]. The projection $\Pi_{\mathcal{X}}$ enforces the domain constraint while $\eta$ is the ascent step size [§sec_1].

## Go Deeper {#go-deeper}
- Maximum-Margin Objective defines the function being optimized.
- Clean-Data-Free Estimation explains why starts need not be clean examples.
- Order-Statistic p-Value consumes the final per-class maxima.
