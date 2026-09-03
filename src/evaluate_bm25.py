import json
from pathlib import Path

import bm25s

#Files containing the corpus, evaluation queries and relevance judgements.

CORPUS_FILE = Path("data/benchmark_v2/corpus/arxiv_papers.jsonl")
QUERIES_FILE = Path("data/benchmark_v2/eval/queries.jsonl")
QRELS_FILE = Path("data/benchmark_v2/eval/qrels.jsonl")

#Evaluate only the first K retrieved documents for each query.
K = 5


#Load a JSONL file as a list of Python dictionaries.
# Each non-empty line in a JSONL file contains one JSON object.

def load_jsonl(path):
    records = []

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                records.append(json.loads(line))

    return records

def main():
    papers = load_jsonl(CORPUS_FILE)
    queries = load_jsonl(QUERIES_FILE)
    qrels = load_jsonl(QRELS_FILE)

    # Use title + abstract as the retrieval representation.
    # This is the same document representation used by the dense baseline,
    # making the two retrieval systems directly comparable.

    documents = [
        paper["title"] + " " + paper["abstract"]
        for paper in papers
    ]

    # Tokenize and index the corpus using the Lucene-style BM25 variant.
    # No stemming or stopword removal is applied in the current baseline.

    corpus_tokens = bm25s.tokenize(
        documents,
        stopwords=None,
        stemmer=None,
    )

    retriever = bm25s.BM25(method="lucene")
    retriever.index(corpus_tokens)

    judged_query_ids = {
        qrel["query_id"]
        for qrel in qrels
    }

    reciprocal_ranks = []

    for query_record in queries:
        query_id = query_record["query_id"]

        if query_id not in judged_query_ids:
            continue

        query_text = query_record["query"]

        # Build a lookup table from arXiv ID to binary relevance judgment
        # for the current query.
        # A value of 1 means relevant, 0 means non-relevant.
        # Documents absent from this dictionary are unjudged.

        judgments = {
            qrel["arxiv_id"]: qrel["relevance"]
            for qrel in qrels
            if qrel["query_id"] == query_id
        }

        # Retrieve the top-K documents for the current query.

        query_tokens = bm25s.tokenize(
            query_text,
            stopwords=None,
            stemmer=None,
        )

        results, scores = retriever.retrieve(
            query_tokens,
            k=K,
        )

        retrieved_ids = [
            papers[document_index]["arxiv_id"]
            for document_index in results[0]
        ]

        # Do not interpret unjudged documents as non-relevant.
        # If any retrieved document lacks a relevance judgment, skip metric
        # computation for this query rather than silently assigning relevance 0.

        unjudged_ids = [
            arxiv_id
            for arxiv_id in retrieved_ids
            if arxiv_id not in judgments
        ]

        print(f"{query_id}: {query_text}")

        if unjudged_ids:
            print(f"Precision@{K}: not computed")
            print(f"Unjudged retrieved papers: {len(unjudged_ids)}")
            print()
            continue

        # Count how many of the top-K retrieved documents are relevant.

        relevant_retrieved = sum(
            judgments[arxiv_id] == 1
            for arxiv_id in retrieved_ids
        )

        # Count all relevant documents currently known for this query.
        # Because the qrels were created through BM25+dense pooling rather than
        # exhaustive assessment of the full corpus, this denominator represents
        # known relevant documents in the judgment pool, not necessarily every
        # relevant document in the corpus.

        pooled_relevant = sum(judgments.values())

        pooled_recall_at_k = (
            relevant_retrieved / pooled_relevant
            if pooled_relevant > 0
            else 0.0
        )

        precision_at_k = relevant_retrieved / K

        # Reciprocal Rank depends only on the position of the first relevant result.
        # For example, a first relevant result at rank 4 gives RR = 1/4 = 0.25.
        
        first_relevant_rank = next(
        (
            rank
            for rank, arxiv_id in enumerate(retrieved_ids, start=1)
            if judgments[arxiv_id] == 1
        ),
        None,
        )

        if first_relevant_rank is None:
            reciprocal_rank = 0.0
        else:
            reciprocal_rank = 1 / first_relevant_rank

        reciprocal_ranks.append(reciprocal_rank)
        ###############


        print(f"Relevant retrieved: {relevant_retrieved}/{K}")
        print(f"Precision@{K}: {precision_at_k:.3f}")
        print(f"Pooled Recall@{K}: {pooled_recall_at_k:.3f}")
        print(f"RR@{K}: {reciprocal_rank:.3f}")
        print()

    mrr_at_k = sum(reciprocal_ranks) / len(reciprocal_ranks)
    print(f"MRR@{K}: {mrr_at_k:.3f}")

if __name__ == "__main__": 
    main()

