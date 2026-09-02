# Mathematical Literature Retrieval Benchmark

A reproducible information-retrieval benchmark for comparing lexical, dense, and hybrid retrieval methods on technical mathematical literature.

The project investigates how well different retrieval paradigms handle mathematical terminology, specialized concepts, and domain-specific information needs.

## Question

How do lexical, dense, and hybrid retrieval methods compare when searching highly technical mathematical research literature?

In particular, the project aims to study cases where:

* exact terminology is a strong relevance signal;
* mathematically related papers use different vocabulary;
* identical terms occur in different mathematical contexts;
* queries range from narrow known-item-like searches to broader topical searches.

## Current corpus

The current pilot corpus contains **104 arXiv papers**.

Each paper is stored as a JSONL record containing:

* arXiv ID
* title
* abstract
* authors
* publication and update dates
* arXiv categories
* PDF URL
* entry URL

For retrieval experiments, the current searchable document representation is:

```text
title + abstract
```

Other metadata is retained but is not currently used for ranking.

The corpus is intentionally small at this stage so that retrieval behavior and relevance judgments can be inspected manually before scaling the benchmark.

## Retrieval methods

### BM25 lexical baseline

A working BM25 baseline has been implemented using `bm25s`.

Current configuration:

* BM25 variant: Lucene
* searchable fields: title + abstract
* stemming: disabled
* stopword removal: disabled
* ranking depth for the pilot evaluation: top 5

Keeping preprocessing minimal provides a transparent lexical baseline. Stemming, stopword removal, and mathematical-text-specific preprocessing can later be investigated as controlled experimental variables.

### Planned methods

* dense embedding retrieval
* hybrid lexical + dense retrieval
* optional reranking

The goal is to evaluate all retrieval methods against the same corpus, queries, and human relevance judgments.

## Evaluation methodology

Queries are stored separately from relevance judgments.

Each query contains:

* a stable query ID;
* the literal query string given to the retrieval system;
* where needed, a description of the underlying information need.

Human relevance judgments (`qrels`) assign corpus documents binary labels:

```text
1 = relevant
0 = non-relevant
```

An important distinction is maintained between **non-relevant** and **unjudged** documents. The evaluation code does not automatically treat an unjudged document as non-relevant.

The current five-query set is a **pilot evaluation set** intended to develop and test the methodology before building a larger benchmark.

## Pilot BM25 results

Current Precision@5 results are:

| Query ID | Query                    | Precision@5 |
| -------- | ------------------------ | ----------: |
| q001     | geometric knot theory    |       0.800 |
| q002     | finite total curvature   |       0.200 |
| q003     | Symmetric critical point |       0.800 |
| q004     | regularity theory        |       0.600 |
| q005     | Palais-Smale             |       1.000 |

These numbers should be interpreted cautiously.

For example, `finite total curvature` is a narrow query for which the corpus may contain very few relevant documents. If only one document is relevant and it is retrieved at rank 1, Precision@5 is necessarily only 0.2 even though the retrieval behavior may be excellent.

For this reason, Precision@k will not be used in isolation in the final benchmark. Planned evaluation includes metrics appropriate to different information needs, such as:

* Recall@k
* Mean Reciprocal Rank (MRR)
* nDCG

The relevance judgments are also currently based on a small pilot set and should not yet be interpreted as a complete benchmark.

## Repository structure

```text
.
├── data/
│   ├── eval/
│   │   ├── queries.jsonl
│   │   └── qrels.jsonl
│   └── raw/
│       └── arxiv_papers.jsonl
├── src/
│   ├── collect_arxiv.py
│   ├── inspect_corpus.py
│   ├── search_bm25.py
│   └── evaluate_bm25.py
├── README.md
└── requirements.txt
```

## Setup

Create and activate a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the project dependencies:

```bash
python -m pip install -r requirements.txt
```

## Running BM25 search

With the virtual environment activated:

```bash
python src/search_bm25.py "geometric knot theory"
```

The script returns the highest-ranked papers together with their BM25 scores and lexical diagnostics.

## Running the pilot evaluation

```bash
python src/evaluate_bm25.py
```

The evaluator reads the corpus, queries, and human relevance judgments and computes Precision@5 for queries whose retrieved documents have been judged.

## Reproducibility principles

The project is being developed with an emphasis on reproducibility.

In particular:

* raw corpus data is kept separate from retrieval transformations;
* retrieval inputs are defined explicitly;
* package versions are pinned in `requirements.txt`;
* queries and relevance judgments are version controlled;
* retrieval configurations are made explicit rather than relying on hidden defaults;
* unjudged and non-relevant documents are treated differently;
* methodological decisions are developed on a small pilot before scaling experiments.

## Roadmap

Near-term work:

1. strengthen the evaluation methodology;
2. distinguish different query types and information needs;
3. add suitable ranking metrics such as MRR and Recall@k;
4. expand and improve the relevance-judgment pool;
5. implement a dense retrieval baseline;
6. compare lexical and dense retrieval;
7. implement and evaluate hybrid retrieval;
8. expand the mathematical corpus, potentially including literature from a Zotero library.

## Status

**Current milestone:** five-query BM25 pilot benchmark with manually curated relevance judgments and automatic Precision@5 evaluation.

The project is under active development and the current results are preliminary.

