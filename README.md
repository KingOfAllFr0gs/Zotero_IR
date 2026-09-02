# Mathematical Literature Retrieval Benchmark

A small, reproducible benchmark for evaluating information-retrieval methods on mathematical research literature.

The project currently compares a classical lexical retrieval baseline, **BM25**, with a **dense embedding retrieval** baseline on a curated corpus of arXiv papers.

The longer-term goal is to study how different retrieval approaches behave on mathematically specialized information needs and to build a careful evaluation framework for mathematical literature search.

---

## Research Question

How well do standard information-retrieval methods retrieve relevant mathematical papers for specialized mathematical queries?

In particular, the current benchmark compares:

* **BM25 lexical retrieval**
* **Dense semantic retrieval**

Future experiments may include hybrid lexical-semantic retrieval and stronger retrieval models.

---

## Corpus

The current corpus contains **104 arXiv papers**.

Each paper is stored in:

```text
data/raw/arxiv_papers.jsonl
```

with fields including:

* arXiv ID
* title
* abstract
* authors
* publication date
* update date
* categories
* PDF URL
* arXiv entry URL

For retrieval, the document representation is explicitly defined as:

```text
title + abstract
```

The remaining fields are treated as metadata.

Basic corpus validation confirms that all 104 documents contain non-empty titles and abstracts.

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
├── src/
│   ├── collect_arxiv.py
│   ├── inspect_corpus.py
│   ├── inspect_embeddings.py
│   ├── search_bm25.py
│   ├── search_dense.py
│   ├── evaluate_bm25.py
│   └── evaluate_dense.py
├── requirements.txt
└── README.md
```

---

## BM25 Baseline

The lexical baseline uses:

```text
bm25s==0.3.11
```

with the Lucene-style BM25 implementation:

```python
method="lucene"
```

Current preprocessing intentionally remains minimal:

* no stemming
* no stopword removal
* title and abstract concatenated as the searchable document

This provides a simple and interpretable lexical baseline before introducing additional preprocessing choices.

Example:

```bash
python src/search_bm25.py "geometric knot theory"
```

The search script reports the top-ranked papers together with their BM25 scores.

Diagnostic functionality has also been used to inspect matched query terms and document frequencies.

---

## Dense Retrieval Baseline

The dense baseline uses Sentence Transformers with:

```text
sentence-transformers/all-MiniLM-L6-v2
```

Documents and queries are independently encoded into dense vectors.

Embeddings are normalized:

```python
normalize_embeddings=True
```

and retrieval scores are computed using the dot product:

```python
document_embeddings @ query_embedding
```

Because the vectors are normalized, this is equivalent to cosine similarity.

Example:

```bash
python src/search_dense.py "geometric knot theory"
```

The dense baseline deliberately uses a small, general-purpose pretrained model rather than a mathematics-specific model. This provides a useful generic semantic baseline against which later models can be compared.

---

## Evaluation Queries

The current pilot benchmark contains five manually defined information needs.

### q001 — geometric knot theory

Papers concerning geometric or variational properties of knots, such as knot energies, curvature, regularity, or geometric optimization.

Discrete or combinatorial knot models are excluded when they are not primarily concerned with geometric analysis.

### q002 — finite total curvature

Papers in which curves of finite total curvature, or closely related geometric consequences of finite total curvature, are a substantive topic.

### q003 — Symmetric critical point

Papers concerning symmetric critical points or symmetric critical configurations in geometric knot theory and knot-energy problems.

### q004 — regularity theory

Papers developing or applying regularity theory in geometric knot theory, knot energies, or related variational problems.

### q005 — Geometric Gradient flow

Papers where gradient flow is studied in a geometric or geometric-variational setting, including flows of geometric objects or geometric energy functionals.

Gradient-flow methods from unrelated areas such as quantum field theory, machine learning, statistical mechanics, and information theory are excluded.

The queries are stored in:

```text
data/eval/queries.jsonl
```

---

## Relevance Judgments

Human relevance judgments are stored in:

```text
data/eval/qrels.jsonl
```

Binary relevance is currently used:

```text
1 = relevant
0 = non-relevant
```

A document with no judgment is treated as **unjudged**, not automatically as non-relevant.

This distinction is important because the relevance set is currently produced through retrieval pooling rather than exhaustive assessment of every query-document pair.

### Pooling Procedure

The initial relevance pool was constructed from BM25 results.

The pool was then expanded using dense retrieval so that the benchmark would not define relevance solely from documents found by BM25.

Current pooling includes approximately:

* BM25 top 20 for q001–q004
* BM25 top 30 for q005
* dense top 20 for all five queries

Only previously unjudged query-document pairs were manually assessed when expanding the pool.

This produces a more balanced evaluation set, although the judgments are still not exhaustive over all 104 documents.

---

## Current Metrics

The benchmark currently reports:

* **Precision@5**
* **Reciprocal Rank@5**
* **Mean Reciprocal Rank@5**

Recall is not yet reported as ordinary exhaustive recall because the relevance judgments were produced through pooling.

A pooled recall measure is planned as the next evaluation step.

---

## Pilot Results

### Precision@5

| Query    |      BM25 | Dense |
| -------- | --------: | ----: |
| q001     |     0.800 | 0.800 |
| q002     |     0.200 | 0.200 |
| q003     | **0.800** | 0.600 |
| q004     |     0.600 | 0.600 |
| q005     |     0.200 | 0.200 |
| **Mean** | **0.520** | 0.480 |

### Reciprocal Rank@5

| Query |  BM25 |     Dense |
| ----- | ----: | --------: |
| q001  | 0.500 | **1.000** |
| q002  | 1.000 |     1.000 |
| q003  | 1.000 |     1.000 |
| q004  | 1.000 |     1.000 |
| q005  | 0.250 | **1.000** |

### Mean Reciprocal Rank@5

```text
BM25:  0.750
Dense: 1.000
```

These preliminary results already illustrate an important distinction between retrieval objectives.

BM25 currently achieves slightly higher mean Precision@5, meaning that it retrieves slightly more relevant documents within the first five results.

Dense retrieval, however, places a relevant paper at **rank 1 for all five pilot queries**, giving it an MRR@5 of 1.0.

For example, on q005 both methods have:

```text
Precision@5 = 0.200
```

but their first relevant documents occur at very different ranks:

```text
BM25 RR@5  = 0.250
Dense RR@5 = 1.000
```

Thus Precision@k and Reciprocal Rank capture different aspects of retrieval quality.

The current dataset is still small, so these results should be interpreted as pilot observations rather than general conclusions about lexical versus dense retrieval.

---

## Running the Evaluation

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Run the BM25 evaluation:

```bash
python src/evaluate_bm25.py
```

Run the dense evaluation:

```bash
python src/evaluate_dense.py
```

---

## Setup

Create and activate a Python virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

---

## Reproducibility Principles

The project is being developed incrementally with explicit methodological choices.

Current principles include:

* keep corpus construction separate from retrieval
* define the searchable document representation explicitly
* keep retrieval baselines simple before adding complexity
* distinguish unjudged documents from non-relevant documents
* avoid constructing ground truth from a single retrieval system
* record relevance judgments explicitly
* use multiple evaluation metrics
* avoid interpreting pooled judgments as exhaustive ground truth
* commit coherent experimental milestones with Git

The purpose is not merely to obtain good retrieval scores, but to make the experimental procedure understandable and reproducible.

---

## Current Status

Completed:

* arXiv corpus collection
* corpus inspection and validation
* BM25 retrieval baseline
* command-line BM25 search
* BM25 diagnostics
* five-query pilot evaluation set
* binary human relevance judgments
* Precision@5 evaluation
* Reciprocal Rank and MRR evaluation
* dense embedding inspection
* dense retrieval baseline
* dense evaluation
* dense top-20 relevance pooling
* initial BM25 versus dense comparison

---

## Roadmap

Near-term steps:

1. implement pooled Recall@k
2. compare BM25 and dense retrieval under the expanded relevance pool
3. inspect retrieval errors query by query
4. consider additional ranking metrics
5. investigate hybrid lexical-semantic retrieval
6. experiment with stronger or mathematics-oriented embedding models
7. expand the query set and corpus
8. move toward more comprehensive relevance judgments

Because the corpus currently contains only 104 papers, exhaustive relevance assessment may eventually be feasible for a larger-quality evaluation set.

---

## Project Status

This repository is an experimental research project under active development.

The current five-query benchmark is intentionally small. Its purpose is to establish a correct and reproducible evaluation pipeline before scaling to larger corpora, more queries, and more sophisticated retrieval systems.
