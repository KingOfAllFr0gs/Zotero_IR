# Benchmark Design

This document describes the construction of the mathematical literature retrieval benchmark, including corpus design, query formulation, relevance judgments, pooling, and benchmark versioning.

The central design principle is:

> **Benchmark quality before model complexity.**

The goal is to establish a small but methodologically transparent benchmark before introducing increasingly sophisticated retrieval models.

---

## 1. Benchmark Goal

The benchmark evaluates information-retrieval systems on specialized mathematical research literature.

The central research question is:

> How well do standard lexical and semantic retrieval methods retrieve mathematically relevant research papers for specialized mathematical information needs?

The benchmark is designed to support comparisons between:

* lexical retrieval methods such as BM25;
* dense semantic retrieval;
* future hybrid retrieval approaches;
* stronger or mathematics-specific embedding models;
* reranking methods.

At the current stage, benchmark construction and relevance quality are treated as higher priorities than model complexity.

---

## 2. Benchmark Versions

The project contains two benchmark phases:

```text
data/
├── pilot/
│   ├── corpus/
│   └── eval/
│
└── benchmark_v2/
    ├── corpus/
    └── eval/
```

### 2.1 Pilot benchmark

The original pilot benchmark contains:

```text
104 arXiv papers
5 queries
```

It was used to develop and validate the first complete retrieval and evaluation pipeline.

The pilot data is frozen and should not be modified.

Preserving the pilot as a fixed snapshot makes it possible to reproduce the earlier experimental stage even after the main benchmark has expanded.

---

### 2.2 Benchmark v2

The current benchmark contains:

```text
675 arXiv papers
20 queries
307 current relevance judgments
```

Benchmark v2 reuses the pilot papers and existing judgments where possible while expanding both the corpus and the query set.

The original pilot records are preserved exactly inside the larger experimental workflow.

---

## 3. Corpus Representation

Each corpus record contains the following metadata:

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

The searchable document representation used by both retrieval systems is:

```text
title + abstract
```

Using the same document representation for BM25 and dense retrieval ensures that differences in performance are attributable to the retrieval method rather than to differences in available document content.

---

## 4. Pilot Corpus Construction

The pilot corpus was collected from broad arXiv searches related to topics such as:

* geometric knot theory;
* calculus of variations;
* Palais-Smale theory;
* gradient flows;
* knot energies.

The resulting collection contained 104 unique papers.

The pilot was intentionally small so that the complete retrieval and relevance-assessment workflow could be developed before expanding the benchmark.

---

## 5. Benchmark-v2 Corpus Expansion

Benchmark v2 was seeded with all pilot papers and expanded using broader mathematical discovery searches.

Examples include:

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

These are corpus-discovery searches rather than benchmark evaluation queries.

This distinction is deliberate.

If the corpus were constructed only by issuing the exact benchmark queries, the collection process could artificially favor documents whose language closely matches those queries.

Using broader discovery topics reduces this source of collection bias.

The resulting corpus contains:

```text
675 papers
0 missing titles
0 missing abstracts
0 duplicate base arXiv IDs
```

---

## 6. arXiv Version Handling

arXiv papers may have multiple versions, for example:

```text
2306.07100v1
2306.07100v2
2306.07100v3
```

During corpus expansion, version suffixes are removed for deduplication purposes:

```text
2306.07100v3 → 2306.07100
```

However, existing pilot records are preserved exactly.

This matters because relevance judgments refer to specific versioned arXiv IDs.

Replacing an older benchmark record with a newer arXiv version could therefore invalidate existing qrels or silently change the experimental data.

The expansion process consequently follows this rule:

> If a paper already exists in the benchmark under the same base arXiv ID, preserve the existing benchmark record.

---

## 7. Evaluation Query Design

Benchmark v2 contains 20 information needs.

The first five originated in the pilot:

```text
q001  geometric knot theory
q002  finite total curvature
q003  Symmetric critical point
q004  regularity theory
q005  Geometric Gradient flow
```

The expanded set includes:

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

Each query record contains:

```text
query
description
```

The short query represents what might be entered into a search system.

The description defines the actual information need and specifies what should count as relevant.

---

## 8. Why Query Descriptions Matter

Many mathematical queries are compositional.

For example:

```text
minimal surfaces and variational methods
```

is not equivalent to:

```text
minimal surfaces
```

A paper may be strongly related to minimal surfaces while using complex analysis, probability, or comparison geometry rather than variational methods.

Likewise:

```text
Palais-Smale condition for geometric functionals
```

requires more than merely discussing the Palais-Smale condition.

The geometric restriction must also be substantive.

The benchmark therefore uses the following annotation principle:

> For a compositional information need, every substantive component of the query description should be satisfied.

Query descriptions were defined before ranking inspection so that relevance criteria would not be tailored retrospectively to the behavior of a particular retrieval system.

---

## 9. Relevance Judgments

Relevance judgments are stored as query-document pairs.

The current benchmark uses binary relevance:

```text
1 = relevant
0 = non-relevant
```

A missing query-document pair is considered:

```text
unjudged
```

It is not automatically treated as non-relevant.

This distinction is fundamental because the benchmark does not contain exhaustive judgments for all:

```text
20 × 675
```

possible query-document pairs.

Relevance is also query-specific.

A paper can therefore be relevant for one query and non-relevant for another.

---

## 10. Relevance Pooling

It is impractical to manually judge every document for every query.

The benchmark therefore uses relevance pooling.

The current benchmark-v2 pool is based on:

```text
BM25 top 5
      ∪
dense top 5
```

for each query.

Previously judged pairs are removed before annotation.

Across the 20 queries, the first v2 pooling stage produced:

```text
100 BM25 top-5 pairs
100 dense top-5 pairs
167 unique query-document pairs
154 previously unjudged candidates
```

All 154 new candidates were manually assessed.

These judgments were then merged with previously available pilot judgments.

---

## 11. Why Pool from Multiple Systems?

Building relevance judgments only from one retrieval system can bias the benchmark toward that system.

For example, if only BM25 results were judged, documents retrieved exclusively by dense retrieval could remain unjudged even when they are relevant.

The benchmark therefore constructs pools from multiple retrieval systems.

The current pool combines BM25 and dense retrieval.

Future pooling rounds may include additional systems or deeper ranking depths.

---

## 12. System-Blind Annotation

Annotation candidates deliberately omit:

* retrieval-system identity;
* ranking position;
* BM25 score;
* dense similarity score.

The assessor sees only information relevant to the mathematical judgment:

* query ID;
* query;
* information-need description;
* arXiv ID;
* title;
* abstract.

This reduces the possibility that knowledge of which system retrieved a paper influences the relevance decision.

---

## 13. Annotation Workflow

The annotation workflow consists of three stages.

### Build the candidate pool

```bash
python src/build_pool.py
```

This creates new, system-blind query-document candidates.

### Annotate the candidates

```bash
python src/annotate_pool.py
```

The interface supports:

```text
1 = relevant
0 = non-relevant
s = skip
q = quit
```

Judgments are saved immediately, making the process resumable.

### Merge judgments

```bash
python src/merge_pool_qrels.py
```

The merge tool:

* checks that the pool is complete;
* avoids duplicate judgments;
* does not overwrite existing qrels;
* can safely be rerun.

---

## 14. Relevance Auditing

Initial human judgments are not assumed to be infallible.

Qualitative error analysis revealed several cases where an initial positive label was too permissive.

For example:

```text
gradient estimates under geometric flow
```

were initially mistaken for papers about:

```text
geometric gradient flows
```

Similarly, several generic minimal-surface papers initially received positive judgments for:

```text
minimal surfaces and variational methods
```

despite lacking a substantive variational component.

These cases were corrected after abstract-level review.

This leads to an important methodological principle:

> Retrieval error analysis can also serve as relevance-judgment quality control.

Corrections are versioned explicitly rather than silently hidden.

---

## 15. Current Limitations

The current relevance pool is shallow.

Top-5 pooling is sufficient to judge the current BM25 and dense top-five rankings directly, but it does not provide exhaustive relevance information.

In particular, later error analysis showed that relevant q009 documents existed deeper in the corpus even though neither baseline retrieved them in its top five.

This demonstrates that:

```text
not retrieved by the pooling systems
```

does not imply:

```text
not relevant
```

The next benchmark-development stage is therefore deeper and more consistent pooling across all 20 information needs.

---

## 16. Design Principles

The benchmark currently follows these principles:

1. Preserve benchmark versions rather than silently replacing them.
2. Use identical document content across retrieval systems.
3. Separate corpus discovery from evaluation queries.
4. Define information needs before ranking inspection.
5. Treat missing judgments as unjudged.
6. Pool results from multiple retrieval systems.
7. Hide system identity during relevance annotation.
8. Preserve existing human judgments unless explicitly audited.
9. Record judgment corrections transparently.
10. Improve benchmark quality before increasing model complexity.

The objective is not merely to generate evaluation numbers.

The objective is to create an experimental setting in which those numbers can be interpreted responsibly.
