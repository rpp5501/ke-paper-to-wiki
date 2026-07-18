# Census19, Texas-100X, and Adult Datasets
## TL;DR {#tldr}
These are the three benchmark datasets used to evaluate targeted attribute inference attacks: Census19 (US Census income/demographic records), Texas-100X (hospital discharge records), and Adult (the classic census income dataset). Each pairs a target-model prediction task (income or surgery procedure) with a chosen sensitive attribute (marital status or sex) that the attacker tries to infer.

## Intuition {#intuition}
To study how privacy risk differs across subgroups, the authors need real-world datasets where a model predicts one thing (like income) while an attacker tries to infer something else that's sensitive (like marital status or sex). Using three datasets of different sizes, domains, and sensitive attributes lets the experiments show that disparate vulnerability isn't a quirk of one dataset but a broader pattern across health, census, and demographic data.

## Mechanics {#mechanics}
Census19 is drawn from the 2019 US Census Bureau Database and contains over 1.6 million records with 12 variables; the target task is binary income classification with the threshold raised to $90,000 (from the Adult dataset's $50,000) to account for inflation, and marital status is collapsed into a binary sensitive attribute (Married vs. Single) [§sec_12_1].

Texas-100X extends the Texas-100 hospital dataset from Shokri et al. to 925,128 records from 441 hospitals, using PRINCSURGPROCCODE as the prediction target; since this column has 100 categorical values and the remaining features can't support accurate 100-class classification, it is collapsed into a binary task (top-10 most frequent procedures vs. the rest), with SEXCODE (Male/Female) chosen as the sensitive attribute [§sec_12_1].

The Adult dataset predicts whether an individual earns over $50,000 a year from 48,842 instances and 14 attributes; marital status is again the sensitive attribute, merged into Married (civ-spouse, spouse-absent, AF-spouse) versus Single (divorced, never-married, separated, widowed), and after removing missing values the dataset shrinks to 45,222 records, split into 35,222 for training target models and 10,000 held out to evaluate attacks on same-distribution data outside the training set [§sec_12_1].

## The Math {#the-math}
The local context describes dataset construction and preprocessing choices only; no equations are present for this concept [§sec_12_1].

## Go Deeper {#go-deeper}
No research note or additional resources are attached to this concept.
