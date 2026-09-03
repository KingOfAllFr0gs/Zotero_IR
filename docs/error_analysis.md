# Retrieval Error Analysis

This document records qualitative error analysis for the BM25 and dense retrieval baselines.

The purpose of error analysis is not merely to explain why one aggregate score is larger than another.

It serves three roles:

1. identify systematic retrieval failure modes;
2. understand when lexical or semantic retrieval is preferable;
3. audit the quality and consistency of relevance judgments.

---

## 1. Why Qualitative Error Analysis Is Necessary

The current aggregate results are:

| Metric           |  BM25 |     Dense |
| ---------------- | ----: | --------: |
| Mean Precision@5 | 0.520 | **0.660** |
| MRR@5            | 0.687 | **0.817** |

These numbers show that dense retrieval performs better overall on the current benchmark.

They do not explain:

* why dense retrieval succeeds;
* where BM25 remains stronger;
* whether the systems make different kinds of mistakes;
* whether the relevance labels themselves are consistent.

For this reason, representative query rankings are inspected directly.

---

## 2. Ranking Comparison Tool

Individual queries can be inspected using:

```bash
python src/compare_rankings.py q012
```

The script prints:

* query ID;
* query text;
* information-need description;
* BM25 top results;
* dense top results;
* relevance labels;
* BM25 scores;
* dense similarities.

The script is diagnostic only.

It does not modify the benchmark or relevance judgments.

---

## 3. q005 — Lexical Relation Failure

Query:

```text
Geometric Gradient flow
```

Information need:

> Papers about gradient flows arising from geometric variational problems. Exclude gradient-flow papers from unrelated areas such as quantum field theory, machine learning, statistical mechanics, or information geometry.

BM25 initially retrieved papers with titles such as:

```text
Gradient estimates ... under geometric flow
Gradient estimates ... along geometric flow
Harnack estimates ... under geometric flow
```

These papers contain all of the important lexical terms:

```text
gradient
geometric
flow
```

but the terms occur in the wrong mathematical relationship.

The papers study:

```text
gradient estimates for PDEs evolving under a geometric flow
```

rather than:

```text
a geometric flow arising as a gradient flow of an energy
```

After abstract-level auditing, five initial positive judgments were corrected to non-relevant.

Current performance:

```text
BM25:
P@5 = 0.000
RR@5 = 0.000

Dense:
P@5 = 0.600
RR@5 = 1.000
```

### Interpretation

This is a clear **lexical relation failure**.

BM25 recognizes term occurrence but does not directly model the mathematical relationship between those terms.

Dense retrieval performs substantially better because it can capture some semantic structure beyond exact lexical co-occurrence.

---

## 4. q007 — Dense Modifier Failure

Query:

```text
Palais-Smale condition for geometric functionals
```

The key restriction is not merely:

```text
Palais-Smale
```

but:

```text
Palais-Smale in a geometric variational setting
```

Dense retrieval returned several papers strongly related to Palais-Smale theory, including generic work on:

* abstract functionals;
* bounded Palais-Smale sequences;
* critical-point theory;
* generalized Palais-Smale conditions.

These were mathematically related to the central concept but failed the geometric restriction.

Current performance:

```text
BM25:
P@5 = 0.200
RR@5 = 0.200

Dense:
P@5 = 0.000
RR@5 = 0.000
```

### Interpretation

This is a **semantic modifier failure**.

The dense model captures the central semantic concept well but underweights an important restricting modifier.

Dense retrieval is therefore not automatically compositional.

Semantic similarity can produce documents that are broadly related while failing a narrower mathematical condition.

---

## 5. q009 — Shared Retrieval Failure

Query:

```text
Topological methods in calculus of variations
```

Initial top-five results from both systems were non-relevant.

Current top-five performance remains:

```text
BM25:
P@5 = 0.000
RR@5 = 0.000

Dense:
P@5 = 0.000
RR@5 = 0.000
```

This raised an important question:

> Does the corpus actually contain relevant material?

A deeper corpus search was performed using mathematical terminology related to the information need, including:

```text
minimax
Lusternik-Schnirelmann
category
critical groups
Morse index
topological degree
```

Relevant papers were found.

Examples involved:

* Lusternik-Schnirelmann category;
* minimax structures;
* Palais-Smale sequences;
* Morse-index information;
* critical-point theory;
* topological degree methods.

Five additional q009 papers were judged relevant during this analysis.

### Interpretation

q009 is a **shared top-ranking failure**.

The relevant material exists in the corpus, but neither baseline ranks it highly enough.

This case is also important for benchmark methodology.

The original top-5 union pool would have failed to discover these relevant papers because both contributing systems missed them.

Therefore:

> A shallow multi-system pool can still contain systematic blind spots shared by all participating systems.

This is the strongest current motivation for deeper relevance pooling.

---

## 6. q012 — BM25 Compositional Vocabulary Failure

Query:

```text
Morse theory for variational problems
```

BM25 top results included papers matching fragments of the information need, for example:

* papers explicitly containing “Morse theory” but in unrelated mathematical settings;
* generic calculus-of-variations papers;
* combinatorial or algebraic Morse-theory work.

Dense retrieval instead surfaced papers involving:

* Morse index;
* Palais-Smale sequences;
* constrained functionals;
* critical-point methods;
* related variational vocabulary.

Current performance:

```text
BM25:
P@5 = 0.000
RR@5 = 0.000

Dense:
P@5 = 0.600
RR@5 = 1.000
```

### Interpretation

This is a **semantic vocabulary and composition advantage** for dense retrieval.

The relevant literature does not always use the exact phrase:

```text
Morse theory
```

even when it uses closely related concepts such as:

```text
Morse index
critical groups
Palais-Smale sequences
```

Dense retrieval can connect some of these related expressions.

BM25 cannot do so unless the relevant lexical terms overlap directly.

---

## 7. q014 — Lexical Specificity Advantage for BM25

Query:

```text
minimal surfaces and variational methods
```

Initial relevance labels were too permissive.

Several retrieved papers were about minimal surfaces but used other substantive methods, including:

* probability;
* complex analysis;
* comparison geometry;
* Teichmüller-theoretic constructions.

These papers were topically related to minimal surfaces but did not satisfy the variational-method requirement.

After abstract-level auditing, four positive labels were corrected to non-relevant.

Current performance:

```text
BM25:
P@5 = 0.600
RR@5 = 1.000

Dense:
P@5 = 0.400
RR@5 ≈ 0.333
```

### Interpretation

BM25 benefits here from **lexical specificity**.

The exact minimal-surface terminology is highly informative.

Dense retrieval broadens the neighborhood to papers that are semantically close to minimal-surface theory but methodologically outside the information need.

This case demonstrates that dense retrieval's broader semantic matching can sometimes reduce precision.

---

## 8. q019 — Specialized Terminology and Semantic Drift

Query:

```text
Gamma convergence of geometric energies
```

BM25 top results included:

```text
Gamma convergence of a family of surface--director bending energies...
Gamma-convergence of nonlocal energies for partitions...
```

Dense retrieval also found strong relevant results but returned several generic Γ-convergence papers involving:

* gradient flows;
* integral functionals;
* pairs of measures;
* abstract variational convergence.

These papers are close to the general topic of Γ-convergence but do not clearly satisfy the geometric-energy restriction.

Current performance:

```text
BM25:
P@5 = 0.600
RR@5 = 1.000

Dense:
P@5 = 0.400
RR@5 = 1.000
```

### Interpretation

This is another **lexical specificity advantage** for BM25.

When highly distinctive mathematical terminology directly characterizes an information need, exact lexical matching can be particularly effective.

Dense retrieval may instead drift toward a larger semantic neighborhood of conceptually related but insufficiently specific papers.

---

## 9. Emerging Failure Taxonomy

The current analysis suggests several recurring retrieval phenomena.

### 9.1 Lexical relation failure

BM25 can retrieve all important words while missing the intended relationship between them.

Example:

```text
gradient estimates + geometric flow
```

versus:

```text
geometric gradient flow
```

Observed in:

```text
q005
```

---

### 9.2 Lexical vocabulary mismatch

Relevant papers may express a concept using related terminology rather than the literal query phrase.

Example:

```text
Morse index
Palais-Smale sequences
critical groups
```

instead of:

```text
Morse theory for variational problems
```

Observed in:

```text
q012
```

Dense retrieval can benefit in this setting.

---

### 9.3 Dense modifier failure

A dense model may capture the main topic while underweighting a restricting qualifier.

Example:

```text
Palais-Smale
```

without sufficiently enforcing:

```text
geometric functionals
```

Observed in:

```text
q007
```

---

### 9.4 Dense semantic drift

Dense retrieval can broaden into nearby mathematical literature that is conceptually related but outside the exact information need.

Observed in:

```text
q014
q019
```

---

### 9.5 Lexical specificity advantage

Specialized mathematical phrases can make lexical matching highly effective.

Observed in:

```text
q014
q019
```

---

### 9.6 Shared retrieval blind spots

Both lexical and dense systems may miss the same relevant literature.

Observed in:

```text
q009
```

This is particularly important because multi-system pooling does not guarantee complete relevance coverage when the systems share a blind spot.

---

## 10. Error Analysis as Relevance Auditing

The error-analysis process also exposed annotation inconsistencies.

Two important examples were:

### q005

Five papers initially labeled relevant were actually about gradient estimates under geometric flows rather than geometric gradient flows.

Their labels were corrected:

```text
1 → 0
```

### q014

Several papers on minimal surfaces were initially labeled relevant despite lacking a substantive variational component.

Four labels were corrected:

```text
1 → 0
```

These changes were not arbitrary modifications based on system performance.

They were corrections made by returning to the pre-existing information-need descriptions and applying them more consistently.

---

## 11. Lesson for Compositional Queries

Several errors arose because papers satisfied only one part of a multi-part query.

A useful annotation rule emerging from the analysis is:

> Matching the topic is not enough when the information need also specifies a method, setting, or mathematical relationship.

Examples include:

```text
minimal surfaces
+
variational methods
```

and:

```text
Palais-Smale
+
geometric functionals
```

Both components must be substantive.

This principle should be applied consistently in future relevance annotation.

---

## 12. Implications for Future Retrieval Models

The current error patterns suggest several possible improvements.

### Hybrid retrieval

BM25 and dense retrieval exhibit complementary strengths.

A hybrid model could potentially combine:

* BM25's lexical specificity;
* dense retrieval's vocabulary generalization.

### Reranking

A second-stage model might improve compositional reasoning over a smaller candidate set.

For example, it could distinguish:

```text
gradient estimates under geometric flow
```

from:

```text
gradient flow of a geometric energy
```

### Mathematics-specific embeddings

The current dense model is general-purpose.

A model trained on mathematical or scientific literature may represent specialized relationships more accurately.

However, these model improvements should be tested only after the relevance pool is sufficiently robust.

---

## 13. Implications for Pooling

q009 provides direct evidence that top-5 pooling is too shallow for strong recall conclusions.

A deeper pool should likely include:

```text
BM25 top N
      ∪
dense top N
```

for a larger value of \(N\), potentially supplemented by future retrieval systems.

The purpose would not be simply to increase the number of judgments.

It would be to reduce the probability that relevant documents are missed because every participating system shares the same top-ranking failure.

---

## 14. Current Conclusion

Dense retrieval currently outperforms BM25 on aggregate Precision@5 and MRR@5.

However, the qualitative picture is more nuanced:

```text
BM25
→ strong lexical specificity
→ vulnerable to compositional and vocabulary mismatch

Dense retrieval
→ stronger semantic vocabulary matching
→ vulnerable to modifier failure and semantic drift

Both systems
→ capable of sharing retrieval blind spots
```

The most important conclusion from the current stage is therefore not simply:

```text
dense > BM25
```

It is:

> The two retrieval paradigms fail in systematically different ways, and reliable evaluation depends as much on careful relevance construction as on the ranking algorithms themselves.

This motivates the next benchmark milestone: deeper relevance pooling before increasing model complexity.
