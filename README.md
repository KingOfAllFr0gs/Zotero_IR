# Mathematical Literature Retrieval Benchmark

A small, reproducible benchmark for evaluating information-retrieval methods on mathematical research literature.

The project currently compares a classical lexical retrieval baseline, **BM25**, with a **dense semantic retrieval** baseline on a curated corpus of arXiv papers.

The main goal is not simply to maximize retrieval scores, but to build a careful experimental framework for studying mathematical literature retrieval with explicit corpus construction, human relevance judgments, reproducible baselines, and transparent evaluation methodology.

---

## Research Question

How well do standard information-retrieval methods retrieve relevant mathematical papers for specialized mathematical information needs?

The current pilot compares:

* **BM25 lexical retrieval**
* **dense embedding retrieval**

Future experiments may include:

* larger mathematical corpora
* larger and more diverse query sets
* hybrid lexical-semantic retrieval
* stronger retrieval models
* mathematics-oriented embedding models
* reranking methods

The immediate priority, however, is to **expand the benchmark before increasing model complexity**.

---

## Current Pilot Benchmark

The current pilot contains:

```text
104 arXiv papers
5 mathematical queries
binary human relevance judgments
2 retrieval systems
```

The pilot was deliberately kept small so that the complete retrieval and evaluation pipeline could be designed, inspected, and debugged before scaling.

It should therefore be understood primarily as a **methodological pilot**, not as a dataset large enough to support general conclusions about mathematical search.

---

## Corpus

The corpus is stored in:

```text
data/raw/arxiv_papers.jsonl
```

It currently contains **104 unique arXiv papers**.

Each paper contains the following fields:

```text
arxiv_id
title
abstract
authors
published
updated
categories
pdf_url
entry_url
```

For retrieval, the searchable document representation is explicitly defined as:

```text
title + abstract
```

The remaining fields are treated as metadata.

The corpus inspection script confirms that all 104 papers contain non-empty titles and abstracts.

---

## Corpus Construction

The pilot corpus was collected through several broad arXiv searches related to the mathematical themes of the benchmark:

```text
"geometric knot theory"
"calculus of variations"
"Palais-Smale"
"gradient flow"
"knot energy"
```

Up to 25 results were requested for each search.

Papers returned by multiple searches were deduplicated using their arXiv IDs.

The resulting collection contains 104 unique papers.

Corpus construction is implemented in:

```text
src/collect_arxiv.py
```

The resulting fixed corpus is retained as part of the reproducible pilot benchmark.

---

## Repository Structure

```text
.
├── data/
│   ├── raw/
│   │   └── arxiv_papers.jsonl
│   └── eval/
│       ├── queries.jsonl
│       └── qrels.jsonl
│
├── src/
│   ├── collect_arxiv.py
│   ├── inspect_corpus.py
│   ├── inspect_embeddings.py
│   ├── search_bm25.py
│   ├── search_dense.py
│   ├── evaluate_bm25.py
│   └── evaluate_dense.py
│
├── requirements.txt
└── README.md
```

---

# Retrieval Baselines

## BM25

The lexical baseline uses:

```text
bm25s==0.3.11
```

with the Lucene-style implementation:

```python
method="lucene"
```

The current baseline intentionally uses minimal preprocessing:

```text
no stemming
no stopword removal
```

The searchable document is:

```text
title + abstract
```

This produces a simple and interpretable lexical baseline before introducing additional preprocessing choices.

Example search:

```bash
python src/search_bm25.py "geometric knot theory"
```

The script reports:

* document rank
* title
* arXiv ID
* BM25 score
* literal query terms matched by the document

It also reports query-term document frequencies as a simple ranking diagnostic.

These diagnostics are explanatory only and do not affect retrieval.

---

## Dense Retrieval

The dense baseline uses Sentence Transformers with:

```text
sentence-transformers/all-MiniLM-L6-v2
```

The same document representation is used:

```text
title + abstract
```

Documents and queries are encoded independently as dense vectors.

Embeddings are normalized:

```python
normalize_embeddings=True
```

Similarity is calculated using:

```python
document_embeddings @ query_embedding
```

Because both vectors are normalized, their dot product is equivalent to cosine similarity.

Example search:

```bash
python src/search_dense.py "geometric knot theory"
```

The script reports:

* document rank
* title
* arXiv ID
* cosine similarity

The current model is deliberately a small, general-purpose embedding model rather than a mathematics-specific retrieval model.

Its role is to provide a simple semantic baseline against which later systems can be compared.

---

# Pilot Evaluation Set

The evaluation queries are stored in:

```text
data/eval/queries.jsonl
```

The current pilot contains five information needs.

---

## q001 — geometric knot theory

**Query**

```text
geometric knot theory
```

**Information need**

Papers concerning geometric or variational properties of knots, such as knot energies, curvature, regularity, or geometric optimization.

Papers whose primary focus is a discrete or combinatorial knot model rather than geometric analysis are excluded.

---

## q002 — finite total curvature

**Query**

```text
finite total curvature
```

**Information need**

Papers in which curves of finite total curvature, or closely related geometric consequences of finite total curvature, are a substantive topic.

Papers where curvature is only incidental or refers to a substantially different notion are excluded.

---

## q003 — Symmetric critical point

**Query**

```text
Symmetric critical point
```

**Information need**

Papers concerning symmetric critical points or symmetric critical configurations in geometric knot theory and knot-energy problems.

General critical-point theory unrelated to knots or geometric knot energies is excluded.

---

## q004 — regularity theory

**Query**

```text
regularity theory
```

**Information need**

Papers developing or applying regularity theory in geometric knot theory, knot energies, or related variational problems.

Regularity theory unrelated to those settings is excluded.

---

## q005 — Geometric Gradient flow

**Query**

```text
Geometric Gradient flow
```

**Information need**

Papers where gradient flow is studied in a geometric or geometric-variational setting, including flows of geometric objects or geometric energy functionals.

Gradient-flow methods in unrelated areas such as:

* quantum field theory
* machine learning
* statistical mechanics
* information theory

are excluded.

---

# Relevance Judgments

Human relevance judgments are stored in:

```text
data/eval/qrels.jsonl
```

Binary relevance is currently used:

```text
1 = relevant
0 = non-relevant
```

A paper absent from the qrels for a particular query is considered:

```text
unjudged
```

and is **not automatically treated as non-relevant**.

This distinction is important because the current relevance set was constructed through retrieval pooling rather than exhaustive assessment of every query-document pair.

---

# Relevance Pooling

The first relevance judgments were obtained from BM25 rankings.

The pool was later expanded using dense retrieval so that the benchmark would not define relevance solely from documents surfaced by BM25.

The current pool includes approximately:

```text
BM25 top 20 for q001–q004
BM25 top 30 for q005

Dense top 20 for q001–q005
```

When dense retrieval introduced documents already judged through the BM25 pool, they were not judged again.

Only previously unseen query-document pairs were assessed.

This produces a union pool influenced by more than one retrieval system.

The judgment set is therefore substantially better than one derived solely from BM25, although it is still not exhaustive over the complete 104-document corpus.

---

# Evaluation Metrics

The benchmark currently reports:

* **Precision@5**
* **Pooled Recall@5**
* **Reciprocal Rank@5**
* **Mean Reciprocal Rank@5**

---

## Precision@5

Precision@5 measures the fraction of the first five retrieved papers that are relevant:

$$
P@5 =
\frac{\text{relevant papers retrieved in top 5}}{5}.
$$

It measures how much relevant material appears near the top of the ranking.

---

## Reciprocal Rank

Reciprocal Rank depends only on the position of the first relevant result:

$$
RR =
\frac{1}{\text{rank of first relevant result}}.
$$

For example:

```text
first relevant result at rank 1 → RR = 1
first relevant result at rank 2 → RR = 0.5
first relevant result at rank 4 → RR = 0.25
```

Mean Reciprocal Rank averages this quantity over all evaluated queries.

---

## Pooled Recall@5

Ordinary recall would require knowing every relevant document in the corpus.

That is not currently available.

Instead, the benchmark reports:

$$
\text{Pooled Recall@5}
=
\frac{\text{relevant documents retrieved in top 5}}
{\text{known relevant documents in the judgment pool}}.
$$

The word **pooled** is important.

The denominator represents all currently known relevant papers discovered through the BM25+dense pooling process.

It does not necessarily represent every relevant paper in the complete corpus.

The pooled-recall denominator may therefore increase in the future if additional retrieval systems discover previously unjudged relevant documents.

---

# Current Pilot Results

## Precision@5

| Query    |      BM25 | Dense |
| -------- | --------: | ----: |
| q001     |     0.800 | 0.800 |
| q002     |     0.200 | 0.200 |
| q003     | **0.800** | 0.600 |
| q004     |     0.600 | 0.600 |
| q005     |     0.200 | 0.200 |
| **Mean** | **0.520** | 0.480 |

---

## Pooled Recall@5

| Query |      BM25 | Dense |
| ----- | --------: | ----: |
| q001  |     0.200 | 0.200 |
| q002  |     1.000 | 1.000 |
| q003  | **0.444** | 0.333 |
| q004  |     0.429 | 0.429 |
| q005  |     0.333 | 0.333 |

Approximate mean pooled Recall@5:

```text
BM25:  0.481
Dense: 0.459
```

---

## Reciprocal Rank@5

| Query |  BM25 |     Dense |
| ----- | ----: | --------: |
| q001  | 0.500 | **1.000** |
| q002  | 1.000 |     1.000 |
| q003  | 1.000 |     1.000 |
| q004  | 1.000 |     1.000 |
| q005  | 0.250 | **1.000** |

Mean Reciprocal Rank:

```text
BM25 MRR@5:  0.750
Dense MRR@5: 1.000
```

---

# Preliminary Interpretation

The pilot results show different strengths for the two retrieval approaches.

BM25 currently has slightly higher:

```text
mean Precision@5
mean pooled Recall@5
```

while dense retrieval has substantially higher:

```text
MRR@5
```

Dense retrieval places a relevant document at **rank 1 for all five current queries**.

BM25 does not.

However, dense retrieval does not simply dominate BM25.

For example, on q003:

```text
BM25 relevant documents in top 5:  4
Dense relevant documents in top 5: 3
```

Thus BM25 has higher Precision@5 and pooled Recall@5 for that query even though both systems retrieve a relevant document at rank 1.

q005 gives another useful example.

Both systems have:

```text
Precision@5 = 0.200
```

but:

```text
BM25 RR@5  = 0.250
Dense RR@5 = 1.000
```

Thus the two systems retrieve the same number of relevant documents within the top five, but dense retrieval places the relevant paper much earlier.

These examples demonstrate why multiple retrieval metrics are required.

No strong general conclusion about lexical versus dense retrieval should yet be drawn from only five queries.

---

# Running the Project

Create a Python virtual environment:

```bash
python -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Inspect the Corpus

```bash
python src/inspect_corpus.py
```

The current corpus should report:

```text
Number of papers: 104
Papers with missing titles: 0
Papers with missing abstracts: 0
```

---

## BM25 Search

```bash
python src/search_bm25.py "geometric knot theory"
```

---

## Dense Search

```bash
python src/search_dense.py "geometric knot theory"
```

---

## BM25 Evaluation

```bash
python src/evaluate_bm25.py
```

---

## Dense Evaluation

```bash
python src/evaluate_dense.py
```

---

# Implementation Notes

The project code is intentionally kept relatively simple.

The current focus is on making methodological decisions explicit rather than prematurely optimizing the implementation.

The core scripts now contain comments documenting important choices including:

* corpus construction
* document representation
* preprocessing
* BM25 configuration
* dense-vector normalization
* similarity computation
* treatment of unjudged documents
* pooled recall
* reciprocal rank
* relevance pooling

JSONL loading code also ignores blank lines so that accidental whitespace does not break corpus or evaluation-file parsing.

---

# Reproducibility Principles

The project follows several explicit principles.

### Keep corpus construction separate from retrieval

The corpus is collected once and stored locally.

Retrieval systems operate on the same fixed corpus.

### Use the same document representation

Both BM25 and dense retrieval use:

```text
title + abstract
```

This avoids confounding retrieval-method differences with different input representations.

### Establish simple baselines first

BM25 and a small general-purpose embedding model are used before introducing sophisticated retrieval methods.

### Treat unjudged documents correctly

Unjudged documents are not silently interpreted as non-relevant.

### Avoid single-system ground truth

Relevance judgments are pooled from more than one retrieval system.

### Use multiple metrics

Precision, pooled recall, and reciprocal rank capture different aspects of retrieval behavior.

### Distinguish pooled evaluation from exhaustive evaluation

The current relevance judgments are incomplete.

Metric names and interpretation explicitly reflect this limitation.

### Preserve experimental milestones

Git commits are used to checkpoint coherent stages of the benchmark.

---

# Current Status

The initial pilot benchmark is now operational.

Completed:

* arXiv corpus collection
* duplicate removal
* corpus inspection and validation
* fixed title+abstract document representation
* BM25 retrieval baseline
* BM25 ranking diagnostics
* dense embedding inspection
* dense retrieval baseline
* five manually defined mathematical information needs
* binary human relevance judgments
* BM25 relevance pooling
* dense top-20 relevance pooling
* Precision@5 evaluation
* Reciprocal Rank evaluation
* MRR@5 evaluation
* pooled Recall@5 evaluation
* BM25 versus dense comparison
* code documentation and cleanup
* defensive JSONL blank-line handling

At this stage, the principal limitation is no longer the evaluation pipeline itself.

The main limitation is **benchmark size**.

---

# Next Benchmark Phase

The next phase will focus on expanding the benchmark before introducing substantially more sophisticated retrieval systems.

The current pilot has two major limitations:

```text
104 documents
5 queries
```

Both should increase.

The query count is especially important because retrieval comparisons are ultimately evaluated across information needs.

With only five queries, aggregate scores can change substantially because of the behavior of a single query.

The current pilot will therefore be preserved as a reproducible checkpoint rather than continuously transformed into a much larger experiment.

A larger second-stage benchmark will be developed from the lessons learned here.

A tentative next target is:

```text
20–30 carefully defined mathematical queries
several hundred papers
```

The exact size will depend partly on the amount of human relevance assessment required.

---

# Roadmap

Near-term priorities:

1. preserve the current pilot benchmark as a stable reference point;
2. design a larger and more diverse set of mathematical information needs;
3. expand the mathematical corpus reproducibly;
4. run BM25 and dense retrieval over the expanded benchmark;
5. construct a new relevance pool using multiple retrieval systems;
6. perform human relevance assessment;
7. evaluate Precision, pooled Recall, RR, MRR, and potentially additional ranking metrics;
8. conduct systematic query-by-query error analysis.

After the benchmark has been expanded:

9. investigate hybrid lexical-semantic retrieval;
10. experiment with stronger embedding models;
11. investigate mathematics-oriented retrieval models;
12. consider reranking methods;
13. study larger-scale mathematical literature retrieval.

Possible future evaluation improvements include:

* graded relevance judgments
* nDCG
* deeper ranking cutoffs
* exhaustive judgments for smaller subsets
* larger query sets
* cross-topic evaluation
* inter-annotator agreement if additional assessors are introduced

---

# Experimental Philosophy

The project intentionally prioritizes **benchmark quality before model complexity**.

The development strategy is:

```text
build a small benchmark
        ↓
validate corpus construction
        ↓
validate relevance judgments
        ↓
establish simple retrieval baselines
        ↓
validate evaluation metrics
        ↓
expand the benchmark
        ↓
analyze retrieval behavior
        ↓
introduce more sophisticated systems
```

This order is deliberate.

A sophisticated retrieval model is difficult to evaluate meaningfully if the benchmark itself contains too few queries or poorly understood relevance judgments.

The goal is therefore not merely to obtain higher retrieval scores.

The goal is to construct an experimental setting in which improvements can eventually be interpreted with confidence.

---

# Project Status

This repository is an experimental research project under active development.

The first pilot benchmark now provides a complete end-to-end pipeline:

```text
arXiv collection
→ corpus inspection
→ lexical retrieval
→ dense retrieval
→ human relevance assessment
→ pooled judgments
→ quantitative evaluation
```

The next major milestone is **benchmark expansion**, with particular emphasis on increasing the number and diversity of mathematical information needs before drawing broader conclusions about retrieval-system performance.
