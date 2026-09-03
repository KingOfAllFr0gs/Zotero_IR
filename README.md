# Mathematical Literature Retrieval Benchmark

A reproducible benchmark for evaluating information-retrieval methods on mathematical research literature.

The project compares classical lexical retrieval with dense semantic retrieval on curated arXiv corpora and manually defined mathematical information needs.

The emphasis is not only on retrieval scores, but on building a transparent experimental framework with:

* reproducible corpus construction;
* explicit query definitions;
* human relevance judgments;
* multi-system relevance pooling;
* careful treatment of unjudged documents;
* multiple retrieval metrics;
* qualitative error analysis;
* versioned benchmark phases.

The project currently contains a frozen **pilot benchmark** and a larger **benchmark v2**.

---

# Research Question

How well do standard information-retrieval methods retrieve relevant mathematical papers for specialized mathematical information needs?

The current retrieval baselines are:

* **BM25 lexical retrieval**
* **dense semantic retrieval**

The longer-term goal is to investigate:

* hybrid lexical-semantic retrieval;
* stronger embedding models;
* mathematics-specific retrieval models;
* reranking methods;
* larger mathematical corpora and query sets.

The current priority remains **benchmark quality before model complexity**.

---

# Benchmark Versions

## Pilot Benchmark

The original pilot benchmark is preserved as a frozen experimental snapshot.

```text
104 arXiv papers
5 queries
BM25 baseline
dense baseline
human relevance judgments
BM25+dense relevance pooling
```

The pilot data is stored under:

```text
data/pilot/
├── corpus/
│   └── arxiv_papers.jsonl
└── eval/
    ├── queries.jsonl
    └── qrels.jsonl
```

The pilot is no longer modified.

Its purpose is to preserve the exact data used during development of the initial retrieval and evaluation pipeline.

---

## Benchmark v2

The active benchmark is substantially larger:

```text
675 arXiv papers
20 queries
307 current query-document relevance judgments
BM25 retrieval
dense retrieval
system-blind relevance pooling
```

Benchmark-v2 data is stored under:

```text
data/benchmark_v2/
├── corpus/
│   └── arxiv_papers.jsonl
└── eval/
    ├── queries.jsonl
    ├── qrels.jsonl
    └── pool_candidates.jsonl
```

The original 104 pilot papers are included in the v2 corpus.

This allows judgments from q001–q005 to be reused where the same versioned arXiv paper remains present.

New papers remain unjudged until they enter a relevance-assessment pool.

---

# Repository Structure

```text
.
├── data/
│   ├── pilot/
│   │   ├── corpus/
│   │   │   └── arxiv_papers.jsonl
│   │   └── eval/
│   │       ├── queries.jsonl
│   │       └── qrels.jsonl
│   │
│   └── benchmark_v2/
│       ├── corpus/
│       │   └── arxiv_papers.jsonl
│       └── eval/
│           ├── queries.jsonl
│           ├── qrels.jsonl
│           └── pool_candidates.jsonl
│
├── src/
│   ├── collect_arxiv.py
│   ├── expand_corpus.py
│   ├── inspect_corpus.py
│   ├── inspect_embeddings.py
│   ├── search_bm25.py
│   ├── search_dense.py
│   ├── evaluate_bm25.py
│   ├── evaluate_dense.py
│   ├── build_pool.py
│   ├── annotate_pool.py
│   ├── merge_pool_qrels.py
│   └── compare_rankings.py
│
├── requirements.txt
└── README.md
```

---

# Corpus Representation

Each arXiv paper stores:

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

Both retrieval systems use the same searchable representation:

```text
title + abstract
```

All other fields are treated as metadata.

Using the same representation ensures that differences between BM25 and dense retrieval arise from the retrieval method rather than different document content.

---

# Corpus Construction

## Pilot Corpus

The pilot corpus was constructed from broad arXiv searches around:

```text
geometric knot theory
calculus of variations
Palais-Smale
gradient flow
knot energy
```

Duplicate papers were removed using arXiv IDs.

This produced 104 unique papers.

---

## Benchmark-v2 Expansion

Benchmark v2 was seeded with the complete pilot corpus and expanded using broader discovery searches including:

```text
geometric analysis
calculus of variations
critical point theory
geometric measure theory
concentration compactness
Morse theory
harmonic maps
minimal surfaces
isoperimetric problem
Sobolev inequalities
free boundary
geometric flow
Gamma convergence
spectral geometry
nonlinear elliptic equations
```

These are **corpus-construction queries**, not evaluation queries.

They are deliberately broader than the benchmark information needs so that the corpus is not constructed solely from the exact wording used during evaluation.

Up to 40 arXiv results were requested for each discovery query.

The resulting benchmark-v2 corpus contains:

```text
675 unique papers
```

with:

```text
0 missing titles
0 missing abstracts
0 duplicate base arXiv IDs
```

---

# arXiv Version Handling

Existing pilot records are preserved exactly, including their versioned arXiv IDs.

For deduplication during corpus expansion, version suffixes are removed conceptually:

```text
2505.02719v2   → 2505.02719
math/0606007v2 → math/0606007
```

If a newer arXiv version is encountered during expansion, an existing benchmark record is retained rather than replaced.

This is important because relevance judgments refer to specific versioned arXiv IDs.

---

# Retrieval Baselines

## BM25

The lexical baseline uses:

```text
bm25s==0.3.11
```

with:

```python
method="lucene"
```

Current preprocessing is intentionally minimal:

```text
no stemming
no stopword removal
```

Example:

```bash
python src/search_bm25.py "geometric knot theory"
```

The search script reports:

* rank;
* title;
* arXiv ID;
* BM25 score;
* matched query terms;
* query-term document frequencies.

The diagnostic information does not affect ranking.

---

## Dense Retrieval

The dense baseline uses:

```text
sentence-transformers/all-MiniLM-L6-v2
```

Documents and queries are encoded as normalized dense vectors:

```python
normalize_embeddings=True
```

Similarity is computed using:

```python
document_embeddings @ query_embedding
```

Because the embeddings are normalized, dot product is equivalent to cosine similarity.

Example:

```bash
python src/search_dense.py "geometric knot theory"
```

The model is intentionally a small, general-purpose baseline rather than a mathematics-specific retrieval model.

---

# Evaluation Queries

Benchmark v2 contains **20 mathematical information needs**.

The first five originate from the pilot benchmark.

```text
q001  geometric knot theory
q002  finite total curvature
q003  Symmetric critical point
q004  regularity theory
q005  Geometric Gradient flow
```

The expanded query set adds:

```text
q006  variational methods in geometric analysis
q007  Palais-Smale condition for geometric functionals
q008  geometric curvature functionals
q009  Topological methods in calculus of variations
q010  existence of minimizers in geometric variational problems
q011  concentration compactness in geometric variational problems
q012  Morse theory for variational problems
q013  harmonic maps and energy minimization
q014  minimal surfaces and variational methods
q015  isoperimetric problems on manifolds
q016  Sobolev inequalities in geometric analysis
q017  free boundary variational problems
q018  singularities in geometric flows
q019  Gamma convergence of geometric energies
q020  variational eigenvalue problems on geometric domains
```

Each query contains both:

```text
query
description
```

The description defines the actual information need and determines relevance.

This is especially important for compositional queries, where matching only one component is insufficient.

---

# Relevance Judgments

Human relevance judgments are stored in:

```text
data/benchmark_v2/eval/qrels.jsonl
```

Binary relevance is currently used:

```text
1 = relevant
0 = non-relevant
```

A missing query-document pair is:

```text
unjudged
```

and is **not automatically treated as non-relevant**.

Relevance is query-specific.

The same paper may therefore be relevant to one query and non-relevant to another.

---

# Relevance Pooling

Benchmark v2 currently uses a system-blind top-5 union pool.

For every query:

```text
BM25 top 5
      ∪
dense top 5
      ↓
remove previously judged pairs
      ↓
human relevance assessment
```

Across the 20 queries:

```text
BM25 top-5 pairs:       100
dense top-5 pairs:      100
combined unique pairs:  167
new judgments required: 154
```

All 154 new candidates were manually assessed.

Together with reused judgments from the pilot phase, benchmark v2 currently contains:

```text
307 relevance judgments
```

---

# System-Blind Annotation

`build_pool.py` deliberately omits:

* retrieval-system identity;
* rank;
* retrieval score

from annotation candidates.

The annotation file contains only:

* query ID;
* query text;
* information-need description;
* arXiv ID;
* title;
* abstract;
* relevance field.

This reduces the possibility that knowing which system retrieved a document influences the human relevance judgment.

---

# Annotation Tools

## Build a Relevance Pool

```bash
python src/build_pool.py
```

This script:

1. runs BM25;
2. runs dense retrieval;
3. constructs their union;
4. removes existing qrels;
5. produces system-blind annotation candidates.

The current pool depth is:

```text
5
```

matching the current evaluation cutoff.

---

## Annotate Candidates

```bash
python src/annotate_pool.py
```

Controls:

```text
1 = relevant
0 = non-relevant
s = skip
q = quit
```

Progress is saved immediately after each judgment.

Previously judged candidates are automatically skipped, making annotation resumable.

Skipping leaves a document genuinely unjudged rather than assigning relevance 0.

---

## Merge Completed Judgments

```bash
python src/merge_pool_qrels.py
```

The merge script:

* refuses to merge incomplete annotation pools;
* never overwrites existing qrels;
* avoids duplicate query-document judgments;
* is safe to rerun.

The frozen pilot qrels are never modified.

---

# Evaluation Metrics

The benchmark currently reports:

* Precision@5;
* Reciprocal Rank@5;
* Mean Reciprocal Rank@5;
* pooled Recall@5.

---

## Precision@5

$$
P@5 =
\frac{\text{relevant papers retrieved in the first five}}
{5}.
$$

---

## Reciprocal Rank

$$
RR =
\frac{1}{\text{rank of the first relevant paper}}.
$$

For example:

```text
rank 1 → RR = 1
rank 2 → RR = 0.5
rank 3 → RR ≈ 0.333
rank 5 → RR = 0.2
```

Mean Reciprocal Rank averages RR across queries.

---

## Pooled Recall@5

$$
\text{Pooled Recall@5}
=
\frac{\text{relevant papers retrieved in the top five}}
{\text{known relevant papers in the judgment pool}}.
$$

This is **not exhaustive recall**.

The denominator contains only currently known relevant documents.

Pooled recall is therefore considered provisional in benchmark v2 because pooling depth is not yet uniform historically:

* q001–q005 inherit deeper pilot judgments;
* q006–q020 currently rely primarily on the top-5 v2 union pool;
* targeted error analysis has already discovered additional relevant documents outside the initial top-five pool.

For this reason, the principal current v2 comparison emphasizes:

```text
Precision@5
RR@5
MRR@5
```

rather than pooled recall.

---

# Current Benchmark-v2 Results

After relevance auditing during qualitative error analysis:

| Metric               |  BM25 |     Dense |
| -------------------- | ----: | --------: |
| **Mean Precision@5** | 0.520 | **0.660** |
| **MRR@5**            | 0.687 | **0.817** |

Dense retrieval currently performs better on both aggregate metrics.

These numbers remain preliminary and should not yet be interpreted as general evidence that dense retrieval is superior for mathematical literature retrieval.

The benchmark still contains only 20 queries, and qualitative behavior varies substantially by query.

---

# Query-Level Behavior

The expanded benchmark reveals several distinct retrieval behaviors.

## q005 — lexical relation failure

Query:

```text
Geometric Gradient flow
```

BM25 retrieved papers about:

```text
gradient estimates under geometric flow
```

These papers contained the individual lexical signals:

```text
gradient
geometric
flow
```

but did not study gradient flows arising from geometric variational problems.

After abstract-level auditing, five originally positive q005 judgments were corrected to non-relevant.

Current q005 performance:

```text
BM25:
P@5 = 0.000
RR@5 = 0.000

Dense:
P@5 = 0.600
RR@5 = 1.000
```

This demonstrates that lexical co-occurrence does not guarantee the correct mathematical relationship between terms.

---

## q007 — semantic modifier failure

Query:

```text
Palais-Smale condition for geometric functionals
```

Dense retrieval strongly captures the central Palais-Smale concept but retrieves generic functional-analytic and critical-point papers that fail the **geometric** restriction.

Current performance:

```text
BM25:
P@5 = 0.200
RR@5 = 0.200

Dense:
P@5 = 0.000
RR@5 = 0.000
```

This illustrates that semantic retrieval may still underweight an important restricting modifier.

---

## q009 — shared retrieval failure

Query:

```text
Topological methods in calculus of variations
```

Both systems currently retrieve:

```text
P@5 = 0.000
RR@5 = 0.000
```

However, deeper inspection showed that the corpus does contain relevant papers involving:

* Lusternik-Schnirelmann category;
* minimax methods;
* Morse-index information;
* critical-point theory;
* topological degree methods.

Five additional relevant q009 papers were identified during error analysis.

Thus q009 is a genuine shared top-ranking failure rather than simply a corpus-coverage failure.

It also demonstrates a limitation of shallow pooling: relevant material may exist even when every system contributing to the initial pool misses it.

---

## q012 — dense semantic/compositional advantage

Query:

```text
Morse theory for variational problems
```

BM25 retrieves papers matching either:

```text
Morse theory
```

or:

```text
variational problems
```

without reliably enforcing the intended relationship between them.

Dense retrieval surfaces papers involving related concepts such as:

* Morse index;
* Palais-Smale sequences;
* constrained functionals;
* critical-point methods.

Current performance:

```text
BM25:
P@5 = 0.000
RR@5 = 0.000

Dense:
P@5 = 0.600
RR@5 = 1.000
```

---

## q014 — lexical specificity advantage

Query:

```text
minimal surfaces and variational methods
```

Abstract-level auditing showed that several papers about minimal surfaces were initially labeled too broadly despite using probabilistic, complex-analytic, or other non-variational methods.

After correcting these judgments:

```text
BM25:
P@5 = 0.600
RR@5 = 1.000

Dense:
P@5 = 0.400
RR@5 ≈ 0.333
```

BM25 benefits here from precise minimal-surface terminology, while dense retrieval admits semantically related but methodologically incorrect papers.

---

# Relevance-Judgment Auditing

Qualitative error analysis revealed that relevance assessment itself requires auditing.

Several initial judgments were overly permissive because papers matched a broad topic without satisfying all components of a compositional information need.

Examples included:

```text
gradient estimates + geometric flow
```

being mistaken for:

```text
geometric gradient flow
```

and generic minimal-surface papers being counted for:

```text
minimal surfaces + variational methods
```

The benchmark therefore treats qualitative retrieval inspection as part of the evaluation methodology rather than merely an optional post-hoc analysis.

A useful principle emerging from this phase is:

> For compositional information needs, every substantive component of the query definition must be satisfied.

---

# Error-Analysis Tool

Rankings can be compared directly using:

```bash
python src/compare_rankings.py q012
```

The script displays:

* the information-need description;
* BM25 top results;
* dense top results;
* relevance labels;
* BM25 scores;
* cosine similarities.

The tool is diagnostic only and does not modify benchmark data.

---

# Running the Benchmark

Create a virtual environment:

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

## Inspect Corpus

```bash
python src/inspect_corpus.py
```

Current benchmark-v2 corpus:

```text
Number of papers: 675
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

# Reproducibility Principles

The project currently follows these principles.

### Version benchmark phases

The pilot is frozen rather than silently transformed into benchmark v2.

### Preserve existing research data

Existing corpus records and relevance judgments are never overwritten unnecessarily.

### Use identical document representations

BM25 and dense retrieval both use:

```text
title + abstract
```

### Separate corpus construction from evaluation queries

Corpus discovery uses broad mathematical searches rather than simply issuing all benchmark queries verbatim.

### Treat unjudged documents correctly

Unjudged does not mean non-relevant.

### Pool from multiple retrieval systems

Ground truth is not constructed solely from BM25 or solely from dense retrieval.

### Blind the relevance assessor to retrieval-system identity

System, score, and rank are omitted from annotation candidates.

### Save human annotation incrementally

Annotation progress is written immediately and can be resumed.

### Audit relevance judgments qualitatively

Error analysis is used both to understand retrieval failures and to detect inconsistent human judgments.

### Avoid overstating pooled recall

Pooled recall is explicitly distinguished from exhaustive recall.

### Preserve coherent experimental milestones with Git

Corpus changes, query changes, pooling, annotation, judgment corrections, and code documentation are committed separately where possible.

---

# Current Status

Completed:

* frozen 104-paper pilot benchmark;
* 675-paper benchmark-v2 corpus;
* 20-query evaluation set;
* BM25 lexical baseline;
* dense semantic baseline;
* corpus inspection and validation;
* arXiv-version-aware corpus expansion;
* BM25+dense top-5 relevance pooling;
* system-blind annotation workflow;
* 154 new v2 pool judgments;
* reuse of pilot relevance data;
* 307 current v2 relevance judgments;
* Precision@5 evaluation;
* RR@5 evaluation;
* MRR@5 evaluation;
* provisional pooled Recall@5 evaluation;
* query-by-query ranking comparison;
* qualitative error analysis;
* relevance-judgment auditing;
* documentation of core and v2 tooling.

---

# Next Steps

The immediate next priority is to strengthen the relevance pool.

The current top-5 pool is sufficient for evaluating the top-five rankings of BM25 and dense retrieval, but q009 demonstrated that relevant documents may exist deeper in the corpus even when both systems fail to retrieve them near the top.

Planned next steps:

1. deepen relevance pooling beyond rank 5;
2. ensure more consistent pooling depth across all 20 queries;
3. continue auditing compositional relevance judgments;
4. recompute pooled Recall@5 using the richer judgment set;
5. perform broader error analysis;
6. investigate additional ranking metrics such as nDCG;
7. only after benchmark stabilization, investigate hybrid lexical-semantic retrieval;
8. experiment with stronger and mathematics-oriented embedding models.

---

# Experimental Philosophy

The project deliberately follows:

```text
build a small benchmark
        ↓
validate retrieval and evaluation
        ↓
freeze the pilot
        ↓
expand corpus and query set
        ↓
construct human relevance judgments
        ↓
audit retrieval and annotation errors
        ↓
deepen evaluation quality
        ↓
only then increase model complexity
```

The goal is not merely to obtain a higher retrieval score.

The goal is to create an experimental setting in which retrieval improvements can eventually be interpreted with confidence.

---

# Project Status

The project has moved beyond its initial pilot phase.

Benchmark v2 now provides an end-to-end workflow:

```text
corpus construction
→ corpus validation
→ lexical retrieval
→ dense retrieval
→ multi-system pooling
→ blinded human annotation
→ qrel integration
→ quantitative evaluation
→ qualitative error analysis
→ relevance auditing
```

The next major milestone is **deeper and more consistent relevance assessment across the 20-query benchmark** before introducing substantially more sophisticated retrieval systems.
