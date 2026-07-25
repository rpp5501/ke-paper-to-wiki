import json
import re
from pathlib import Path

from paper_skill.p4_write import write_pages

OUT = Path(__file__).resolve().parent


def page(title, tldr, intuition, mechanics, math, deeper):
    return f"""# {title}

## TL;DR {{#tldr}}
{tldr}

## Intuition {{#intuition}}
{intuition}

## Mechanics {{#mechanics}}
{mechanics}

## The Math {{#the-math}}
{math}

## Go Deeper {{#go-deeper}}
{deeper}
""".replace("\u00c2\u00a7", "\u00a7")


PAGES = {
"universal-post-training-backdoor-detection": page(
    "Universal Post-Training Backdoor Detection (MM-BD)",
    "MM-BD detects a backdoored classifier by searching its pre-softmax logit landscape for a class with an unusually large maximum margin, without assuming the trigger type or using clean samples for detection.",
    "Imagine testing a sealed machine by asking what output it can make when you are allowed to feed it arbitrary inputs. A backdoor target class has learned an unusually reusable route to dominance: many different starting points can be pushed toward a large separation from every competing class. MM-BD treats that geometric oddity as the evidence of compromise.",
    "The detector has two stages. It estimates one maximum-margin statistic per class with multi-start projected gradient ascent, then tests whether the largest statistic is an outlier under a null distribution fitted from the other classes [Â§sec_1]. If the p-value is below the fixed significance level, the class owning the largest statistic is reported as the likely target [Â§sec_1].",
    "For class $c$, the paper's statistic is $$r_c = \\max_{\\mathbf{x}\\in\\mathcal{X}}\\left[g_c(\\mathbf{x})-\\max_{k\\ne c}g_k(\\mathbf{x})\\right]$$ [Â§sec_1]. The detector sets $r_{\\max}=\\max_c r_c$ and uses $$p_v = 1-H_0(r_{\\max})^{K-1}$$ [Â§sec_1].",
    "- Backdoor Threat Model explains what the attacker and defender can access.\n- Maximum-Margin Objective derives the statistic used by the detector.\n- Maximum-Margin Backdoor Mitigation (MM-BM) covers the optional repair path."
),
"backdoor-threat-model": page(
    "Backdoor Threat Model",
    "The paper studies a trained image classifier that behaves normally on clean inputs but routes triggered inputs from one or more source classes to an attacker-chosen target class.",
    "The attack is like hiding a secret instruction in a model's training history. A normal image should be recognized by its ordinary content, but the same small cue repeated during poisoning becomes a shortcut that overrides that content later.",
    "The paper distinguishes basic, advanced, and adaptive attackers. The basic attacker poisons data without seeing the original training set or controlling training; advanced attackers may use surrogate data or training control; an adaptive attacker also knows MM-BD and optimizes against it [Â§sec_1]. The defender receives a trained classifier after training and wants detection first, followed by mitigation if replacement is unavailable [Â§sec_1].",
    "A classical backdoor aims for clean correctness and triggered misclassification simultaneously: $$f(\\mathbf{x})=y_{\\mathrm{true}},\\qquad f(\\tilde{\\mathbf{x}})=t$$ [Â§sec_1]. The paper's threat model makes $t$ an attacker-selected target and allows an arbitrary number of source classes [Â§sec_1].",
    "- Classical Poisoning Mechanism gives the training-time construction.\n- Attacker Capability Ladder compares the three attacker regimes.\n- Empirical Scope and Failure Modes records where the assumptions become fragile."
),
"post-training-defender-constraints": page(
    "Post-Training Defender Constraints",
    "MM-BD is designed for a downstream user who has the trained classifier but no training set, no known trigger, and no clean reference classifier.",
    "This is an inspection problem, not a retraining problem. The defender has the finished artifact and must decide whether its behavior contains a hidden route, even when the evidence used to build the route is gone or proprietary.",
    "The paper lists five assumptions: the defender does not know whether an attack exists, does not know the pattern type, lacks the training set, lacks a clean classifier for comparison, and may not possess clean examples. MM-BD needs no clean samples for detection, although MM-BM later uses a small clean set for accuracy preservation [Â§sec_1].",
    "The detection input is the model itself: $g_c(\\cdot)$ is queried over the input domain $\\mathcal{X}$, while the clean sample set $D$ appears only in the mitigation problem [Â§sec_1]. This separation is the reason the detector can be data-free at inference time [Â§sec_1].",
    "- Clean-Data-Free Estimation shows how random inputs replace a reference dataset.\n- Unsupervised Anomaly Inference shows how a decision is made without labels.\n- Accuracy-Preserving Lagrangian explains the extra data needed for repair."
),
"logit-output-landscape": page(
    "Pre-Softmax Logit Landscape",
    "The logit landscape is the set of class score functions before softmax; MM-BD searches this landscape because a backdoor changes its geometry before probabilities are normalized.",
    "Softmax is a translator that turns scores into probabilities. MM-BD listens to the raw voices before translation, where it can compare how far one class can rise above all others rather than being distracted by normalization.",
    "Let $g_c(\\mathbf{x})$ be the logit for class $c$. For every candidate class, MM-BD asks how large the gap to the strongest rival can become over valid inputs. A backdoor repeats a common feature during poisoning, so the target's score surface can acquire a sharper, more reusable direction than ordinary class evidence [Â§sec_1].",
    "The class margin at an input is $$m_c(\\mathbf{x})=g_c(\\mathbf{x})-\\max_{k\\ne c}g_k(\\mathbf{x})$$ [Â§sec_1]. The landscape statistic is the supremum of this margin over $\\mathcal{X}$, so it measures separability from the strongest competitor rather than the absolute value of one logit [Â§sec_1].",
    "- Maximum-Margin Objective turns the landscape into a statistic.\n- Boosting and Suppression explains the backdoor-induced deformation.\n- Projected Gradient Estimation describes how the search is approximated."
),
"pattern-agnostic-signature": page(
    "Pattern-Agnostic Attack Signature",
    "The proposed signature is not the trigger image itself; it is the unusually large target-class margin produced by repeated backdoor features in the trained model.",
    "Different keys can open the same faulty lock. The pixel pattern may be a patch, noise, a blend, or a more advanced construction, but the repeated association can still leave the same kind of geometric scar in the classifier's output surface.",
    "MM-BD avoids reverse-engineering a patch or assuming a perturbation norm. It optimizes the classifier's margin directly, so the input-space embedding mechanism is treated as an unknown nuisance [Â§sec_1]. The paper argues that even sample-specific triggers can share semantic regularities in latent space, which may preserve detectability [Â§sec_1].",
    "The intended separation is $$r_t \\gg r_c\\quad\\text{for non-target }c$$ [Â§sec_1]. This is a comparative claim about the target statistic among classes, not a guarantee for every attack; the paper explicitly discusses intrinsic backdoors and adaptive attacks as limits [Â§sec_1].",
    "- Trigger-Embedding Families catalogs the explicit image mechanisms used in experiments.\n- Target-Logit Boosting and Non-Target Suppression gives the causal intuition.\n- Adaptive Min-Max Attack shows how an attacker can target the signature."
),
"maximum-margin-objective": page(
    "Maximum-Margin Objective",
    "For every class, MM-BD maximizes the gap between that class's logit and the largest competing logit over valid inputs.",
    "Instead of asking whether a class can shout loudly, ask whether it can shout while silencing the loudest rival. That contest is harder for ordinary neighboring classes and becomes conspicuous when a backdoor target has learned an over-specialized route.",
    "The estimation stage solves one optimization problem per class. It uses the full input domain as the search space, performs multiple random starts, and keeps the largest local optimum found for that class [Â§sec_1]. The resulting $r_c$ values are the only model-derived features needed by the unsupervised detector [Â§sec_1].",
    "The core program is $$\\underset{\\mathbf{x}\\in\\mathcal{X}}{\\operatorname{maximize}}\\;g_c(\\mathbf{x})-\\max_{k\\in\\mathcal{Y}\\setminus\\{c\\}}g_k(\\mathbf{x})$$ [Â§sec_1]. Comparing against the maximum rival makes the statistic robust to classes whose logits rise together, a failure mode the paper illustrates for logit-only alternatives [Â§sec_1].",
    "- Projected Gradient Estimation explains the numerical solver.\n- Null Distribution of Class Margins consumes one statistic per class.\n- Order-Statistic p-Value converts the maximum into a decision."
),
"unsupervised-anomaly-inference": page(
    "Unsupervised Anomaly Inference",
    "MM-BD declares an attack when the largest class margin is too atypical under a one-sided null fit to the remaining class margins.",
    "Suppose a panel of thermometers contains one reading far above the rest. You do not need a labeled example of a faulty thermometer to ask whether that maximum is plausible under the distribution of the other readings.",
    "After computing all $r_c$, the method selects $r_{\\max}$ and fits $H_0$ using the other $K-1$ statistics. The paper uses a one-sided density such as a Gamma distribution because the estimated margins are positive [Â§sec_1]. A detection is made when the order-statistic p-value is below $\\theta$, with $\\theta=0.05$ in the experiments [Â§sec_1].",
    "The p-value is $$p_v=1-H_0(r_{\\max})^{K-1}$$ [Â§sec_1]. Under the no-attack null, the paper states that this order-statistic p-value is uniform on $[0,1]$, so the nominal detection confidence is $1-\\theta$ when $p_v<\\theta$ [Â§sec_1].",
    "- Null Distribution of Class Margins details the leave-one-out fit.\n- Order-Statistic p-Value explains the exponent $K-1$.\n- Empirical Scope and Failure Modes covers false positives and class imbalance."
),
"activation-bound-mitigation": page(
    "Maximum-Margin Backdoor Mitigation (MM-BM)",
    "MM-BM repairs a detected model by capping layer activations with optimized upper bounds, while trying to preserve clean predictions and leaving the learned weights unchanged.",
    "A trigger can work because a small set of internal signals becomes unusually large. MM-BM puts a ceiling above every signal: high enough that ordinary examples still pass, but low enough to suppress the extreme activation pattern that carries the backdoor.",
    "The method applies a separate upper-bound vector to each layer after the first. It optimizes these bounds on a small clean set, constrains clean accuracy to stay above a benchmark, and then applies softmax to the bounded logits [Â§sec_1]. The paper reports effective mitigation for most tested patterns, with weaker results for very small chessboard perturbations [Â§sec_1].",
    "For layer $l$, the bounded activation is $$\\bar{\\sigma}_l(\\mathbf{a};\\mathbf{z}_l)=\\min\\{\\sigma_l(\\mathbf{a}),\\mathbf{z}_l\\}$$ [Â§sec_1]. The min is componentwise, so $\\mathbf{z}_l$ supplies one ceiling per neuron rather than one global clipping value [Â§sec_1].",
    "- Per-Neuron Activation Upper Bounds gives the architecture-level operation.\n- Accuracy-Preserving Lagrangian gives the optimization objective.\n- Empirical Scope and Failure Modes records the mitigation caveats."
),
"classical-poisoning-mechanism": page(
    "Classical Poisoning Mechanism",
    "A classical backdoor poisons training by embedding a common pattern in source-class samples, relabeling them to a target class, and mixing them into the training set.",
    "The attacker teaches the model a second rule: ordinary content maps normally, but the repeated mark overrides that content. Because only a small portion of training data needs the mark, clean behavior can remain apparently intact.",
    "The paper's classical protocol collects source-class samples, embeds the same pattern, relabels those samples to the target, and inserts them for poisoning [Â§sec_1]. The trained classifier is evaluated with clean accuracy and attack success rate, so stealth means preserving the first while increasing the second [Â§sec_1].",
    "For an additive trigger $\\mathbf{v}$, one image-level abstraction is $$\\tilde{\\mathbf{x}}=[\\mathbf{x}+\\mathbf{v}]_c$$ [Â§sec_1]. The target behavior can be summarized as $f(\\mathbf{x})=y$ on clean inputs but $f(\\tilde{\\mathbf{x}})=t$ on triggered inputs [Â§sec_1].",
    "- Trigger-Embedding Families compares additive, patch, and blend mechanisms.\n- Backdoor Threat Model places poisoning in the attacker capability ladder.\n- Pattern-Agnostic Attack Signature explains why MM-BD does not reconstruct the poison."
),
"trigger-embedding-families": page(
    "Trigger-Embedding Families",
    "The experiments include additive patterns, patch replacement patterns, and blended patterns, while MM-BD uses none of these mechanisms as a detection assumption.",
    "A trigger may be a faint watermark, a small pasted object, or a transparent overlay. A detector tied to one visual recipe can miss the others; MM-BD instead looks for the model-side consequence shared by their repeated use.",
    "The paper describes additive perturbations, local patch replacement, and blending with a mask and factor. Its experiments also include chessboard, 1-pixel, BadNet, unicolor, and blend variants [Â§sec_1]. The detector optimizes over images directly, so it need not decide which embedding family generated a suspicious model [Â§sec_1].",
    "The patch abstraction is $$\\tilde{\\mathbf{x}}=(1-\\mathbf{m})\\odot\\mathbf{x}+\\mathbf{m}\\odot\\mathbf{u}$$ [Â§sec_1]. A blended pattern is represented as $$\\tilde{\\mathbf{x}}=(1-\\alpha\\mathbf{m})\\odot\\mathbf{x}+\\alpha\\mathbf{m}\\odot\\mathbf{u}$$ [Â§sec_1].",
    "- Pattern-Agnostic Attack Signature explains the invariant MM-BD uses.\n- Classical Poisoning Mechanism explains how any family becomes training evidence.\n- Empirical Scope and Failure Modes reports cross-pattern performance."
),
"attacker-capability-ladder": page(
    "Basic, Advanced, and Adaptive Attackers",
    "The paper evaluates increasingly capable attackers, from classical poisoning to attackers who control training and explicitly optimize against MM-BD.",
    "Think of three adversaries. One can slip notes into the training pile. Another can rehearse with a surrogate model. The strongest knows the detector's test and changes training so the backdoor works while its geometric fingerprint is less obvious.",
    "A basic attacker can poison data but lacks the original training samples and process control. An advanced attacker may gather data or control training. An adaptive attacker has full training control and full knowledge of MM-BD, so it can add a margin-suppressing term to its objective [Â§sec_1].",
    "The adaptive setting makes the attacker solve a nested problem of the form $$\\min_{\\phi}\\;L_{\\mathrm{clean}}(\\phi)+L_{\\mathrm{backdoor}}(\\phi)+\\beta_M L_M(t;\\phi)$$ [Â§sec_1]. The paper defines $L_M$ as the target class's maximum margin, so increasing $\\beta_M$ pressures the attack to hide the detector's signal [Â§sec_1].",
    "- Adaptive Min-Max Attack expands the last rung into an explicit objective.\n- Backdoor Threat Model describes the defender's target.\n- Empirical Scope and Failure Modes summarizes the cost and trade-offs of evasion."
),
"clean-data-free-estimation": page(
    "Clean-Data-Free Estimation",
    "Detection does not need legitimate images: it generates random valid inputs and optimizes the inspected classifier's logits directly.",
    "A conventional inspector compares a suspicious model with trusted examples. MM-BD instead asks the model to reveal its own strongest class separation, using random probes as starting points rather than semantic samples.",
    "For each class, the detector initializes inputs randomly inside the valid domain, performs projected gradient ascent on the margin, and retains the largest local solution across starts [Â§sec_1]. The paper emphasizes that this avoids the clean-sample requirement of many reverse-engineering detectors [Â§sec_1].",
    "The optimization uses only $g_c$ and $\\mathcal{X}$: $$r_c=\\max_{\\mathbf{x}\\in\\mathcal{X}}m_c(\\mathbf{x})$$ [Â§sec_1]. The clean set $D$ is absent from this expression; it enters only the separate MM-BM mitigation constraint [Â§sec_1].",
    "- Post-Training Defender Constraints defines the information boundary.\n- Projected Gradient Estimation explains the random-probe solver.\n- Unsupervised Anomaly Inference explains why labels are unnecessary."
),
"boosting-and-suppression": page(
    "Target-Logit Boosting and Non-Target Suppression",
    "Repeated backdoor features can both boost the target logit and suppress competing logits, producing the margin anomaly MM-BD measures.",
    "A backdoor is not merely a louder target class. It can also make the alternatives quieter when the model sees the feature combination associated with the poison. The margin captures both effects in one comparison.",
    "The paper attributes the abnormal target margin to overfitting on a common poisoned feature. It contrasts this with ordinary class-discriminating features, which vary across examples and therefore do not create the same reusable direction [Â§sec_1]. The appendix shows why maximizing only a target logit can create false detections when semantically neighboring classes rise together [Â§sec_1].",
    "For a target $t$, the relevant contrast is $$g_t(\\mathbf{x})-\\max_{k\\ne t}g_k(\\mathbf{x})$$ [Â§sec_1]. In the paper's linearized argument, confident clean and triggered classifications imply a target-versus-source response to the trigger of at least $2\\tau$ under the stated assumptions [Â§sec_1].",
    "- Pre-Softmax Logit Landscape provides the geometric view.\n- Maximum-Margin Objective formalizes the two-sided comparison.\n- Empirical Scope and Failure Modes notes intrinsic backdoors that can mimic this effect."
),
"projected-gradient-estimation": page(
    "Projected Gradient Estimation",
    "MM-BD approximates each maximum margin with gradient ascent from multiple random initializations, projecting every iterate back into the valid input set.",
    "Finding the highest hill in a complicated landscape depends on where you start. Multiple starts give the search several chances, while projection keeps the synthetic probe inside the image domain rather than letting it become an invalid input.",
    "For each class, the method runs gradient ascent on the margin objective, uses a convergence criterion, and takes the largest local optimum from 30 random initializations in the main experiments [Â§sec_1]. Projection is appropriate for domains such as pixel boxes, where valid inputs form a closed convex set [Â§sec_1].",
    "A projected update can be written schematically as $$\\mathbf{x}^{(s+1)}=\\Pi_{\\mathcal{X}}\\left(\\mathbf{x}^{(s)}+\\eta\\nabla_{\\mathbf{x}}m_c(\\mathbf{x}^{(s)})\\right)$$ [Â§sec_1]. The projection $\\Pi_{\\mathcal{X}}$ enforces the domain constraint while $\\eta$ is the ascent step size [Â§sec_1].",
    "- Maximum-Margin Objective defines the function being optimized.\n- Clean-Data-Free Estimation explains why starts need not be clean examples.\n- Order-Statistic p-Value consumes the final per-class maxima."
),
"null-margin-distribution": page(
    "Null Distribution of Class Margins",
    "The detector fits a one-sided null distribution to the class margins other than the largest candidate outlier.",
    "If one score is suspiciously high, do not let it teach the reference distribution what normal looks like. MM-BD removes the maximum, then uses the remaining scores as its empirical picture of ordinary class separations.",
    "Let $r_{\\max}$ be the largest class statistic. MM-BD estimates $H_0$ from the other $K-1$ values and uses a positive-support density such as a Gamma distribution [Â§sec_1]. This is an unsupervised reference, not a bank of clean models or labeled attack examples [Â§sec_1].",
    "The null fit is evaluated at $r_{\\max}$ through its cumulative distribution: $$H_0(r_{\\max})=\\Pr_{H_0}(R\\le r_{\\max})$$ [Â§sec_1]. Larger values of the maximum make $1-H_0(r_{\\max})^{K-1}$ smaller, which increases evidence for an attack [Â§sec_1].",
    "- Unsupervised Anomaly Inference puts the fit into the full decision rule.\n- Order-Statistic p-Value explains the multiple-class correction.\n- Empirical Scope and Failure Modes describes small-class-count effects."
),
"order-statistic-pvalue": page(
    "Order-Statistic p-Value",
    "The p-value corrects for selecting the largest among K class statistics, then compares the result with a significance threshold.",
    "Looking at the tallest building in a city is more surprising when the city has only five buildings than when it has thousands. The exponent in the p-value accounts for the fact that MM-BD deliberately searches across all classes for the maximum.",
    "The paper computes the largest statistic, estimates the null from the remaining statistics, and forms an order-statistic p-value [Â§sec_1]. With $\\theta=0.05$, it reports an attack when $p_v<\\theta$ and assigns the target label to the class that produced $r_{\\max}$ [Â§sec_1].",
    "For $K=|\\mathcal{Y}|$, the paper uses $$p_v=1-H_0(r_{\\max})^{K-1}$$ [Â§sec_1]. The associated detection confidence is $1-\\theta$ when the p-value falls below $\\theta$ [Â§sec_1].",
    "- Null Distribution of Class Margins supplies $H_0$.\n- Unsupervised Anomaly Inference explains the threshold decision.\n- Empirical Scope and Failure Modes records the nominal-versus-observed false-positive issue."
),
"adaptive-attack-minimax": page(
    "Adaptive Min-Max Attack",
    "An adaptive attacker can add a penalty on the target maximum margin, but the paper reports a cost in attack success, clean accuracy, optimization time, or some combination.",
    "The attacker is trying to keep two things true at once: the trigger must still work, and the detector must no longer see a tall target hill. Flattening the hill while preserving the backdoor turns training into a harder nested optimization problem.",
    "The adaptive objective adds the target margin to ordinary clean and poisoned cross-entropy training. The paper reports that stronger margin penalties can make attacks undetectable, but also degrade ASR or ACC; a stronger variant that regularizes other classes is even more expensive [Â§sec_1].",
    "With model parameters $\\phi$, the adaptive attack includes $$L_M(t;\\phi)=\\max_{\\mathbf{x}\\in\\mathcal{X}}\\left[g_t(\\mathbf{x};\\phi)-\\max_{k\\ne t}g_k(\\mathbf{x};\\phi)\\right]$$ [Â§sec_1]. The attacker minimizes a weighted sum of clean loss, backdoor loss, and $\\beta_ML_M$ [Â§sec_1].",
    "- Attacker Capability Ladder provides the capability assumptions.\n- Pattern-Agnostic Attack Signature is the quantity being hidden.\n- Empirical Scope and Failure Modes gives the paper's limitation boundary."
),
"per-neuron-upper-bounds": page(
    "Per-Neuron Activation Upper Bounds",
    "MM-BM introduces a separate ceiling for every neuron in selected layers, suppressing abnormally large activations without pruning neurons or changing learned parameters.",
    "A single dimmer switch would be too crude: some neurons naturally need high values while others carry the suspicious burst. Per-neuron ceilings let the repair tighten each channel independently.",
    "The bounded network keeps the original layer functions and parameters but replaces each activation with its componentwise minimum against a bound vector [Â§sec_1]. The paper initializes bounds large enough to avoid initial saturation, then optimizes them downward while monitoring clean accuracy [Â§sec_1].",
    "For layers $l=2,\\ldots,L$, the bound vectors are $\\mathbf{z}_l$. The bounded logit is formed by composing clipped layers, with $$\\bar{\\sigma}_l(\\mathbf{a};\\mathbf{z}_l)=\\min\\{\\sigma_l(\\mathbf{a}),\\mathbf{z}_l\\}$$ [Â§sec_1].",
    "- Activation-Bound Mitigation connects ceilings to the full repair.\n- Accuracy-Preserving Lagrangian explains how ceilings are chosen.\n- Empirical Scope and Failure Modes notes why tiny global perturbations are harder to suppress."
),
"accuracy-preserving-lagrangian": page(
    "Accuracy-Preserving Lagrangian",
    "MM-BM minimizes activation-bound norms while penalizing changes between bounded and original logits on a small clean dataset.",
    "The repair has a safety contract: shrink the internal dynamic range, but do not change ordinary decisions. A Lagrange multiplier acts like a negotiation knob between stronger suppression and fidelity to the original model.",
    "The constrained problem requires clean accuracy to exceed a benchmark such as $\\pi=0.95$. The practical algorithm minimizes a logit-matching loss plus a weighted sum of bound norms, adjusting the multiplier when the accuracy constraint is met or violated [Â§sec_1].",
    "The paper's constraint is $$\\min_{Z}\\sum_{l=2}^{L}\\|\\mathbf{z}_l\\|_2\\quad\\text{subject to}\\quad \\frac{1}{|D|}\\sum_{(\\mathbf{x},y)\\in D}\\mathbf{1}[y=\\arg\\max_c\\bar g_c(\\mathbf{x};Z)]\\ge\\pi$$ [Â§sec_1]. Its Lagrangian adds $$\\lambda\\sum_{l=2}^{L}\\|\\mathbf{z}_l\\|_2$$ [Â§sec_1].",
    "- Per-Neuron Activation Upper Bounds describes $Z$.\n- Activation-Bound Mitigation explains why clean samples are needed only here.\n- Maximum-Margin Backdoor Mitigation (MM-BM) summarizes the algorithmic outcome."
),
"empirical-scope-and-limitations": page(
    "Empirical Scope and Failure Modes",
    "The paper evaluates MM-BD across four image datasets and additional speech and point-cloud settings, while documenting false positives, intrinsic backdoors, and adaptive evasion limits.",
    "A detector can be strong in its intended regime and still have honest blind spots. Here the important question is not only whether the method works on standard poisoned models, but also whether clean training quirks or a determined attacker can produce the same signature.",
    "The main experiments cover CIFAR-10, CIFAR-100, TinyImageNet, and GTSRB with additive, patch, and blended patterns, and compare against NC, TABOR, ABS, PT-RED, META, and TND [Â§sec_1]. The paper reports broadly pattern-invariant detection, but point-cloud performance is weaker in the presence of intrinsic backdoors; class imbalance and deliberately margin-regularized clean models can cause false positives [Â§sec_1].",
    "The nominal false-positive control uses $\\theta=0.05$, but the paper notes that estimating $H_0$ from few classes can make observed rates differ from the nominal level [Â§sec_1]. For adaptive attacks, lowering the target margin can be expressed as an extra term in the attacker objective, creating a direct detector-versus-attacker trade-off [Â§sec_1].",
    "- Adaptive Min-Max Attack details the strongest evasion experiment.\n- Order-Statistic p-Value explains why class count affects calibration.\n- Maximum-Margin Backdoor Mitigation (MM-BM) covers the separate repair results."
),
}


def page_spawn(prompt: str) -> str:
    match = re.search(r"Concept:\s*(.*?)\s+\(level", prompt)
    label = match.group(1).strip() if match else ""
    for cid, text in PAGES.items():
        if text.startswith("# ") and text.splitlines()[0][2:] == label:
            return text
    raise KeyError(f"no Luna page for concept label: {label}")


def main():
    pack = json.loads((OUT / "pack.json").read_text(encoding="utf-8"))
    graph = json.loads((OUT / "concept-graph.json").read_text(encoding="utf-8"))
    toc = json.loads((OUT / "toc.json").read_text(encoding="utf-8"))
    result = write_pages(
        pack,
        graph,
        toc["rows"],
        spawn=page_spawn,
        home=str(OUT / "research-home"),
        out_dir=str(OUT / "pages"),
        workdir=str(OUT / "page-work-retry3"),
    )
    (OUT / "page-generation-report.json").write_text(
        json.dumps({"model": "gpt-5.6-luna", "concept_count": len(PAGES), **result}, indent=1),
        encoding="utf-8",
    )
    if result["failed"] or result["skipped"] or len(result["done"]) != len(PAGES):
        raise SystemExit(result)
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
