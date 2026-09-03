# Evaluation Methodology

This document describes the retrieval baselines, evaluation metrics, current benchmark results, and limitations of the evaluation protocol.

---

## 1. Retrieval Task

Given a mathematical information need, a retrieval system ranks papers from the benchmark corpus.

The current benchmark contains:

```text
675 documents
20 queries
```

Both baseline systems retrieve from the same document representation:

```text
title + abstract
```

This keeps the comparison focused on retrieval methodology rather than differences in document preprocessing.

---

## 2. BM25 Baseline

The lexical retrieval baseline uses:

```text
bm25s
```

with a Lucene-style BM25 implementation.

The current configuration intentionally uses minimal preprocessing:

```text
no stemming
no stopword removal
```

This makes BM25 a simple and interpretable lexical baseline.

A search can be run with:

```bash
python src/search_bm25.py "geometric knot theory"
```

The script reports:

* rank;
* title;
* arXiv ID;
* BM25 score;
* matched query terms;
* query-term document frequencies.

The diagnostic information does not affect ranking.

---

## 3. Dense Retrieval Baseline

The dense baseline uses:

```text
sentence-transformers/all-MiniLM-L6-v2
```

This is a general-purpose sentence embedding model rather than a mathematics-specific retrieval model.

Documents and queries are encoded using normalized embeddings.

Similarity is computed by:

```python
document_embeddings @ query_embedding
```

Because both vectors are normalized, this dot product is equivalent to cosine similarity.

A dense search can be run with:

```bash
python src/search_dense.py "geometric knot theory"
```

The purpose of this baseline is to test whether a simple semantic representation improves over lexical retrieval before introducing stronger specialized models.

---

## 4. Evaluation Cutoff

The current primary evaluation cutoff is:

```text
k = 5
```

This matches the depth of the first benchmark-v2 relevance pool.

Current headline metrics therefore focus on top-five retrieval quality.

---

## 5. Precision@5

Precision@5 measures how many of the first five retrieved papers are relevant:

$$
P@5 =
\frac{\text{number of relevant documents in the top 5}}
{5}.
$$

For example, if three of five retrieved documents are relevant:

$$
P@5 = \frac{3}{5} = 0.6.
$$

Precision@5 measures the quality of the visible top portion of a ranking.

This is particularly appropriate for literature search, where a user may inspect only a small number of highly ranked results.

---

## 6. Reciprocal Rank@5

Reciprocal Rank measures how quickly the system returns its first relevant document.

If the first relevant document occurs at rank \(r\):

$$
RR = \frac{1}{r}.
$$

Examples:

```text
rank 1 → RR = 1.000
rank 2 → RR = 0.500
rank 3 → RR = 0.333
rank 4 → RR = 0.250
rank 5 → RR = 0.200
```

If no relevant document appears in the first five results:

```text
RR@5 = 0
```

---

## 7. Mean Reciprocal Rank@5

Mean Reciprocal Rank averages reciprocal rank across all evaluation queries:

$$
MRR@5 =
\frac{1}{|Q|}
\sum_{q \in Q} RR_q.
$$

MRR therefore measures how reliably a system places at least one relevant result near the top.

It differs from Precision@5 because a system can receive a high reciprocal rank even if the rest of its top-five ranking is poor.

For example:

```text
rank 1 relevant
ranks 2–5 non-relevant
```

gives:

```text
RR@5 = 1.0
P@5  = 0.2
```

The two metrics therefore capture complementary aspects of retrieval quality.

---

## 8. Pooled Recall@5

The evaluation scripts also report pooled Recall@5:

$$
\text{Pooled Recall@5}
=
\frac{\text{known relevant documents retrieved in the top 5}}
{\text{known relevant documents in the qrels}}.
$$

This should not be interpreted as exhaustive recall.

The denominator contains only documents currently known to be relevant.

Documents outside the judgment pool may still be relevant.

For this reason, the project uses the term:

```text
Pooled Recall@5
```

rather than simply:

```text
Recall@5
```

---

## 9. Why Pooled Recall Is Not a Headline Metric Yet

The current judgment depth is not fully uniform.

The first five queries inherit relevance information from the earlier pilot benchmark.

Most later queries were initially judged using the benchmark-v2 top-5 union pool.

In addition, targeted error analysis has introduced some deeper judgments for specific queries.

This means that the number of known relevant documents varies partly because of differences in judgment depth.

More importantly, q009 demonstrated empirically that relevant papers can exist outside the current pool even when both baseline systems miss them near the top.

Therefore the current headline comparison emphasizes:

```text
Mean Precision@5
MRR@5
```

while pooled recall remains provisional.

---

## 10. Current Results

After the current relevance-auditing stage:

| Metric           |  BM25 |     Dense |
| ---------------- | ----: | --------: |
| Mean Precision@5 | 0.520 | **0.660** |
| MRR@5            | 0.687 | **0.817** |

The dense baseline currently performs better on both aggregate metrics.

The difference in mean Precision@5 is:

$$
0.660 - 0.520 = 0.140.
$$

The difference in MRR@5 is:

$$
0.817 - 0.687 = 0.130.
$$

These results indicate a meaningful advantage for the dense baseline on this particular benchmark.

They do not establish that dense retrieval is universally superior for mathematical search.

---

## 11. Query-Level Variation

Aggregate scores hide substantial variation.

Some queries strongly favor dense retrieval.

For example:

```text
q005  Geometric Gradient flow
q012  Morse theory for variational problems
```

Other queries expose weaknesses in dense retrieval.

For example:

```text
q007  Palais-Smale condition for geometric functionals
q014  minimal surfaces and variational methods
q019  Gamma convergence of geometric energies
```

Still others are difficult for both systems:

```text
q009  Topological methods in calculus of variations
```

This variation motivates qualitative ranking analysis rather than relying only on aggregate metrics.

---

## 12. Evaluating BM25

Run:

```bash
python src/evaluate_bm25.py
```

The script:

1. loads the corpus;
2. builds the BM25 index;
3. retrieves the top five documents for each query;
4. checks their existing relevance judgments;
5. computes query-level metrics;
6. reports MRR@5 across evaluated queries.

---

## 13. Evaluating Dense Retrieval

Run:

```bash
python src/evaluate_dense.py
```

The script:

1. loads the corpus;
2. encodes all documents;
3. encodes each query;
4. calculates similarity scores;
5. retrieves the five highest-scoring documents;
6. evaluates against the same qrels used for BM25;
7. reports query-level metrics and MRR@5.

---

## 14. Fair Comparison

Several choices are intended to make the BM25/dense comparison methodologically clean.

### Same corpus

Both systems rank exactly the same 675 documents.

### Same searchable content

Both systems use:

```text
title + abstract
```

### Same queries

Both systems use the same 20 query strings.

### Same relevance judgments

Both systems are evaluated against the same qrels.

### Joint pooling

Relevance judgments are not constructed from only one retrieval system.

### System-blind annotation

The assessor does not know whether a candidate originated from BM25 or dense retrieval.

---

## 15. Score Scales Are Not Comparable

BM25 scores and dense cosine similarities are fundamentally different quantities.

For example:

```text
BM25 score: 5.2
dense similarity: 0.61
```

does not imply that one result is stronger merely because one numerical value is larger.

The two scores should only be interpreted within their own retrieval systems.

Comparison between systems should be based on rankings and evaluation metrics rather than raw score magnitudes.

---

## 16. Statistical Limitations

The current benchmark contains only 20 queries.

This is substantially more informative than the original five-query pilot, but it is still small.

Consequently:

* aggregate results can be influenced strongly by a small number of queries;
* differences should not yet be generalized to mathematical IR as a whole;
* significance testing would have limited power;
* adding high-quality information needs is likely more valuable than immediately adding model complexity.

The benchmark should therefore be interpreted as an experimental testbed rather than a definitive large-scale leaderboard.

---

## 17. Current Evaluation Limitations

The main limitations are:

### Shallow relevance pooling

The initial v2 pool reaches only rank 5.

### Incomplete recall information

Relevant documents outside the current pool may remain unknown.

### Small query set

Twenty queries cannot represent the full diversity of mathematical literature search.

### Binary relevance

The current labels do not distinguish between marginally relevant and highly relevant papers.

### General-purpose dense model

`all-MiniLM-L6-v2` is not specialized for mathematics or scientific retrieval.

These limitations are deliberate targets for later benchmark development.

---

## 18. Planned Evaluation Improvements

Near-term evaluation improvements include:

1. deepen the relevance pool to a consistent depth;
2. reassess pooled recall after deeper judging;
3. add a query-level comparison visualization;
4. consider graded relevance judgments;
5. add ranking metrics such as nDCG;
6. potentially evaluate Recall@10 or Precision@10 after judgment depth supports them;
7. compare future retrieval systems against the same stabilized benchmark.

More sophisticated models should be introduced only after the evaluation framework is strong enough to distinguish genuine improvements from artifacts of incomplete judgments.

---

## 19. Interpretation Principle

The benchmark deliberately distinguishes:

```text
a system retrieved no known relevant document
```

from:

```text
there is no relevant document in the corpus
```

Those statements are not equivalent.

Similarly:

```text
high aggregate score
```

does not imply:

```text
the system understands every mathematical information need well
```

The quantitative evaluation is therefore always interpreted together with qualitative error analysis.
