# Training Hyperparameters and Dataset Sizes

## TL;DR {#tldr}

One frozen backbone, three seeds, and one fixed per-probe recipe: AdamW at $2\times10^{-4}$, batch size $8$, up to $4000$ steps, evaluated every $100$ steps [tab_6]. Dataset sizes range from $301$ synthetic examples per split to $10{,}000$ for the largest natural-language datasets [tab_7].

## Intuition {#intuition}

The base model is frozen throughout: only the per-probe linear head trains, so any difference in probe performance traces to what that head learns, not to a different backbone [§sec_8_4].

Each probe head has its own AdamW optimizer and its own loss, stepped independently on every minibatch — a classification head's gradient never touches a regression head's weights, and vice versa [§sec_8_4].

Holding the recipe — learning rate, batch size, step budget — fixed across every dataset and task type is a methodological choice: it means a performance gap between datasets reflects the data, not a hyperparameter search tuned separately per dataset [§sec_8_4].

## Mechanics {#mechanics}

Table 6 lists the fixed recipe applied to every probe head in the paper and appendix; nothing here varies by dataset, task type, or probe target [tab_6].

| Setting | Value | Notes |
|---|---|---|
| Optimizer (per probe head) | AdamW | one optimizer per active probe head [tab_6] |
| Learning rate | $2 \times 10^{-4}$ | shared across probe heads [tab_6] |
| Weight decay | $0.01$ | [tab_6] |
| Max gradient norm | $10.0$ | gradient clipping [tab_6] |
| Loss (regression) | MSE | for count, percentage, prompt_only_count [tab_6] |
| Loss (classification) | soft cross-entropy | anchor sigma $0.15$ [tab_6] |
| LR scheduler | ReduceLROnPlateau | monitor eval_mae, factor $0.5$, patience $5$ evals, min LR $10^{-7}$ [tab_6] |
| Max steps | $4000$ | [tab_6] |
| Batch size (per device) | $8$ | training and eval, same across probes [tab_6] |
| Gradient accumulation | $1$ | [tab_6] |
| Eval cadence | every $100$ steps | feeds eval_mae to the scheduler [tab_6] |
| Probe input layer | all layers concatenated | data.hidden_layer = "all" [tab_6] |
| Independent seeds | $\{0,1,2\}$ | threaded through Torch/NumPy/Python/HF Trainer/dataloader [tab_6] |
| Hidden-state extraction | frozen forward pass | torch.no_grad() over full (prompt, completion) [tab_6] |
| Generation (extraction) | max_new_tokens $=1024$ | do_sample=True, $T=0.7$, top-$p=0.8$, top-$k=20$ [tab_6] |
| Naturally-terminated filter | has_eos = True only | sequences hitting max_new_tokens excluded [tab_6] |

**Generation for hidden-state extraction is sampled, not greedy:** completions used to build a probe's training and eval examples are drawn with temperature $0.7$ and nucleus/top-$k$ truncation, not the deterministic decoding a reader might assume for a fixed dataset [tab_6].

That means the completion-length distribution feeding each probe is itself a random variable of the sampling settings, not a fixed property of the dataset [tab_6].

The naturally-terminated filter keeps only completions with has_eos = True: any generation that runs out at the $1024$-token cutoff without emitting an end-of-sequence token is excluded before it reaches a probe [tab_6].

Every probe is trained under three independent seeds — $\{0,1,2\}$ — threaded through Torch, NumPy, Python, the HF Trainer, and the dataloader, so a reported number is a summary over three separately-initialized runs, not one [tab_6].

Table 7 gives the configured train/eval split sizes per dataset; the two synthetic tasks are enumerated exhaustively while the five natural-language datasets use fixed slices of their standard splits [tab_7].

| Dataset | Train | Eval | Source / split convention |
|---|---|---|---|
| Count | 301 | 301 | synthetic, $n\in\{0,\ldots,300\}$, one completion per length [tab_7] |
| Countdown | 301 | 301 | synthetic, $n\in\{0,\ldots,300\}$, one completion per length [tab_7] |
| GSM8K | 7,473 | 1,319 | full train/test splits [tab_7] |
| MATH | $\approx7{,}500$ | $\approx5{,}000$ | concatenation of seven subject configs [tab_7] |
| MMLU-Pro | 10,000 | 2,256 | first 10,000 train, last 2,256 eval [tab_7] |
| OpenThoughts-1k | 800 | 200 | first 800 / last 200 of the 1k sample [tab_7] |
| TriviaQA | 10,000 | 2,000 | first 10,000 train, last 2,000 eval [tab_7] |

The configured sizes are upper bounds, not the counts each probe actually trains on: the has_eos filter removes any example whose generation hit the max_new_tokens cutoff, so the effective per-(model, dataset) count varies slightly with the model's own termination behavior [tab_7].

## The Math {#the-math}

**Fixed step and batch settings, not fixed epochs, set the training budget:** max_steps $=4000$ and batch size $=8$ apply identically regardless of how large the train split is, so datasets of very different sizes get very different amounts of repeated exposure [tab_6][tab_7].

- Count / Countdown ($301$ train examples): $4000$ steps $\times\,8 = 32{,}000$ examples seen $\approx 106$ passes over the train set [tab_6][tab_7].
- OpenThoughts-1k ($800$ train): $32{,}000$ examples seen $\approx 40$ passes over the train set [tab_6][tab_7].
- GSM8K ($7{,}473$ train): $32{,}000$ examples seen $\approx 4.3$ passes over the train set [tab_6][tab_7].
- MMLU-Pro / TriviaQA ($10{,}000$ train each): $32{,}000$ examples seen $= 3.2$ passes over the train set [tab_6][tab_7].

The synthetic tasks are trained roughly $33\times$ longer, in epoch terms, than the two largest natural-language datasets — $106$ passes against $3.2$ — even though every probe shares the same optimizer budget [tab_6][tab_7].

**The learning-rate floor is rarely reachable within the step budget:** going from the initial $2\times10^{-4}$ down to the configured minimum $10^{-7}$ needs $\log_2(2{,}000) \approx 11$ halvings of the scheduler's factor-$0.5$ reduction [tab_6].

Each halving needs patience $=5$ evals without improvement, and evals run every $100$ steps, so the fastest possible cadence is one halving per $500$ steps [tab_6].

Over the full $4000$-step budget that allows at most $8$ reductions, taking the learning rate to $2\times10^{-4}/2^{8} \approx 7.8\times10^{-7}$ — within a factor of $8$ of the floor, but never reaching it under this budget [tab_6].

## Go Deeper {#go-deeper}

No research note supplies external resources for this concept; the hyperparameter and dataset-size values above come directly from the paper's tables and the released repository's configuration files [§sec_8_4].
