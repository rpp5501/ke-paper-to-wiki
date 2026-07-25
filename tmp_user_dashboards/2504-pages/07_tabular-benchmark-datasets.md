# Census19, Texas-100X and Adult as target-model training data

## TL;DR {#tldr}

The paper's three datasets are chosen because two of them are big enough to be resampled at exact, controlled correlation levels — the trick every other result in the paper depends on.

Census19 (over 1.6 million US Census records, income classification), Texas-100X (925,128 hospital discharge records, surgery-procedure classification), and Adult (45,222 records after cleaning, income classification) are the three tabular datasets used to train the target models that get attacked throughout the paper. Census19 and Texas-100X are large enough that the authors can subsample them to hit an exact, pre-specified correlation between the sensitive attribute and the output label — both for the dataset as a whole and for individual groups within it. Adult is too small for that trick and is used instead, unmodified, as a check that the findings hold up on a realistic dataset nobody tuned.

## Intuition {#intuition}

Every experiment in this paper needs to answer a causal question: does raising the correlation between a sensitive attribute and a model's output actually make attribute inference attacks work better? Answering that convincingly requires being able to dial that correlation up and down like a knob while holding everything else fixed. You cannot do that with a dataset as it naturally occurs — real-world correlations are whatever they are, and you cannot ask reality to hand you nine versions of the same population at nine different correlation levels.

That is the role Census19 and Texas-100X play. They are large enough (roughly a million records each) that the authors can carve out subsets with a chosen correlation baked in by construction, both across an entire training set and within a single subgroup — Male records at one correlation, Female records at another, in the same experiment. Adult cannot support this because it is small (45,222 records after preprocessing) and was already stretched thin in prior work just to train a reasonably accurate model. So Adult is used the plain way: no controlled sampling, just the dataset as it exists, standing in for "does any of this survive contact with a real, uncurated dataset."

Each dataset also supplies a natural binary sensitive attribute and a natural binary output, which is what the paper's core attacks (CSMIA, LOMIA) and its angular-difference measurement are built around. Census19 uses marital status (Married vs. Single, collapsed from a multi-valued field) as the sensitive attribute and a \$90,000 income threshold as the output. Texas-100X uses SEXCODE as the sensitive attribute and collapses a 100-way surgical-procedure code into "top-10 most frequent procedure" vs. "everything else." Adult uses the same marital-status collapse as Census19, following the preprocessing of prior work on these attacks.

## Mechanics {#mechanics}

**Census19.** Sourced from the 2019 US Census Bureau database, it contains over 1.6 million records with 12 demographic variables. The classification task is income above \$90,000 — adjusted upward from the Adult dataset's \$50,000 threshold to account for inflation. Marital status is the sensitive attribute, collapsed from its original multi-valued form into a binary Married/Single split during preprocessing [§sec_12_1].

**Texas-100X.** Built on the Texas-100 hospital discharge dataset, expanded to 925,128 records from 441 hospitals. The output attribute is PRINC_SURG_PROC_CODE, a categorical field with up to 100 values; because the other columns don't carry enough signal to support reliable 100-class classification, the paper projects it down to a binary problem — top-10 most frequent procedures versus the rest. SEXCODE is the sensitive attribute [§sec_12_1].

**Adult.** The standard UCI Adult dataset (48,842 instances, 14 attributes), used to predict income above \$50,000. Following the preprocessing from Mehnaz et al.'s prior work, marital status is merged into Married (civilian spouse, spouse absent, armed-forces spouse) versus Single (divorced, never-married, separated, widowed) and used as the sensitive attribute. After dropping records with missing values, 45,222 records remain, split 35,222 for training and 10,000 for evaluation [§sec_12_1].

**Why the size split matters mechanically.** For both Census19 and Texas-100X, the paper selects 50,000 records for training and another 50,000 disjoint records for testing, out of pools with roughly a million records available — leaving enormous headroom to resample at arbitrary target correlations without running out of data [§sec_6_1]. This headroom is what makes the paper's correlation-controlled sampling technique possible in the first place — a method that computes exact counts of records needed in each sensitive-value/output-label cell to hit a target Pearson correlation. Adult has no such headroom; it is used at full size, without resampling, which is precisely the point of including it — a sanity check unaffected by the paper's own experimental control [§sec_6_1].

**Group structure used later.** These datasets aren't only split by their primary sensitive attribute — they are also divided into many groups by a separate non-sensitive attribute, which is what lets the paper study *disparity* rather than just average vulnerability. Census19 is split into 51 groups by State; Texas-100X into 10 groups by PAT_STATUS [§sec_6_3]. That grouping, layered on top of the datasets described here, is the substrate for the disparity inference attack and the targeted attacks built on it.

## The Math {#the-math}

This page has no equations of its own — the datasets are infrastructure, not a formal claim. The relevant formalism (the correlation-controlled sampling technique that this page's dataset choices make possible) is defined in [§sec_11_1] and used throughout [§sec_6_1] and [§sec_6_3]; see the `correlation-controlled-sampling` concept for the derivation.

## Go Deeper {#go-deeper}

- **[§sec_6_1] Experimental Setup** — the sampling technique that turns Census19/Texas-100X's size into precise correlation control, and the 50,000/50,000 train/test split.
- **[§sec_11_1] Correctness Proof of Sampling Technique** — the derivation showing the sampling counts actually produce the target correlation.
- **[§sec_6_3] Disparity Inference Attack Performance** — where these datasets get split into 51 and 10 groups respectively, the setup this page's datasets exist to support.
- **[§sec_12_1] Datasets** — the source appendix this page is drawn from, with full preprocessing detail for all three datasets.
- Related concepts: `correlation-controlled-sampling` for the sampling method these datasets' scale enables, `attribute-inference-attack` for the attack these datasets are targets for.
