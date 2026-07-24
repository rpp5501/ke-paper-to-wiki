# Confidence matrix: querying one record under every sensitive value

## TL;DR {#tldr}

To measure how risky a record is, the attacker asks the model the same question once for every possible version of the person's secret and writes all the answers down in one row.

The confidence matrix is the raw material every later measurement in this paper is built from. For each record in a dataset, the adversary swaps in each candidate value of the sensitive attribute one at a time, queries the black-box model, and records the confidence score it returns. Stacked across all records, those rows form a matrix — one row per record, one column per possible secret value — and that matrix is what the angular difference, the disparity ranking, and the targeted attacks all consume as input.

## Intuition {#intuition}

Imagine handing a fortune teller the same question about a person's life, but each time you ask, you feed them one extra fabricated detail — "assume this person is married," then "assume this person is single" — and you write down how confident the fortune teller sounds each time, not what they actually predict. If the fortune teller sounds noticeably more confident under one fabricated detail than another, that's a clue about which detail lines up with reality, or at least with whatever pattern the fortune teller learned to expect.

The confidence matrix is exactly that log, done systematically and at scale. For every record, query the model once per possible sensitive value, and keep the confidence score each time — not the label, the number that says how sure the model was. One row of the matrix belongs to one record; its entries are the confidence scores the model gave under each hypothetical version of that record's secret. Nothing in this step requires knowing the record's real secret value, an auxiliary dataset, or anything about the training data — it's built entirely from queries the attacker is already allowed to make.

What makes the matrix useful isn't any single row — it's what the rows look like when grouped and compared, which is the subject of the angular-difference measurement built directly on top of this matrix.

## Mechanics {#mechanics}

**Move 1 — generate the variants.** For each record \(x\) in the target dataset, the adversary builds a set \(T(x)\) of variant records, one per possible sensitive attribute value, each identical to \(x\) except for the substituted sensitive value [§sec_5].

**Move 2 — query and record confidence.** Each variant in \(T(x)\) is submitted to the black-box target model, and the model's confidence score for its own predicted output is stored — not the predicted label itself. This produces one row of confidence scores per record, with as many entries as there are possible sensitive values [§sec_5_1].

**Move 3 — track which records are usable.** Alongside the matrix, the process produces a correctness indicator per record marking whether at least one of the variant queries returned the correct class label. Records failing this check are still queried, but only records passing it are kept for the next stage of analysis, because the paper's hypothesis is that confidence differences are informative specifically for records the model handles correctly under at least one hypothetical [§sec_5_1].

**Move 4 — hand off to angular difference.** The filtered confidence matrix, split by class label, is what regression lines get fit to when computing angular difference — the matrix itself carries no notion of correlation or vulnerability yet; it is purely the observational log that the next measurement interprets [§sec_5_1].

**Move 5 — the cost this imposes.** Building the matrix costs one query per candidate sensitive value per record, so its total query cost scales with dataset size times the number of possible sensitive values. This cost is exactly why the single-attribute targeted attack introduces a separate query budget \(q\) to cap how many records get the full treatment before an attribute is chosen [§sec_5_3_1].

## The Math {#the-math}

Let \(\mathbb{D}\) be a dataset of \(n\) records, \(\mathcal{M}\) the target model, and \(\mathcal{S}\) the set of \(|\mathcal{S}|\) possible sensitive attribute values. For a record \(x \in \mathbb{D}\) with non-sensitive portion \(n(x)\), define its variant set:

$$
T(x) = \big\{\, (n(x),\, s) \;:\; s \in \mathcal{S} \,\big\}
$$

The confidence matrix \(C\) has dimension \(n \times |\mathcal{S}|\), with one row per record and one column per candidate sensitive value:

$$
C[x,\, s] \;=\; \Pr\big(\mathcal{M}(n(x),\, s)\big), \qquad x \in \mathbb{D},\ s \in \mathcal{S}
$$

where \(\Pr(\mathcal{M}(\cdot))\) is the model's confidence score for its own top prediction on that query [§sec_5].

Alongside \(C\), the process produces a boolean correctness vector \(t\) over records:

$$
t[x] \;=\; \mathbb{1}\Big[\, \exists\, s \in \mathcal{S} : \mathcal{M}(n(x), s) = y(x) \,\Big]
$$

marking whether at least one variant query returned the record's true class label \(y(x)\) [§sec_5_1]. The submatrix of \(C\) restricted to rows with \(t[x]=1\) and a given class label \(y\), written \(C_y\), is the input to the angular-difference computation described in the next stage of the pipeline — this matrix definition stops short of interpreting the numbers, it only specifies how they are collected.

## Go Deeper {#go-deeper}

- **[§sec_5] Attack Methodology** — the formal setup shared by both algorithms built on the confidence matrix: matrix generation and angular-difference computation.
- **[§sec_5_1] Computing Angular Difference** — the immediate next step, where this matrix's rows are turned into regression lines and a single angular-difference number per group.
- **[§sec_5_3_1] Single Attribute-based Targeted Attack** — where the query budget \(q\) is introduced specifically to bound how many records get the full confidence-matrix treatment.
- Related concepts: `angular-difference` for what the matrix is measured for, `confidence-score-gap` for the intuition behind why confidence varies across sensitive-value substitutions in the first place, and `csmia` for an attack that queries records under varying sensitive values in a closely related way.
