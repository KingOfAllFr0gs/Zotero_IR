import json
from pathlib import Path


# Completed system-blind annotation records produced during relevance pooling.
CANDIDATES_FILE = Path(
    "data/benchmark_v2/eval/pool_candidates.jsonl"
)

# Active relevance judgments for benchmark v2.
#
# The frozen pilot qrels live separately under data/pilot/ and are never
# modified by this script.
QRELS_FILE = Path(
    "data/benchmark_v2/eval/qrels.jsonl"
)


def load_jsonl(path):
    """Load a JSONL file into a list of Python dictionaries."""

    records = []

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                records.append(json.loads(line))

    return records


def save_jsonl(path, records):
    """Write a list of Python dictionaries to a JSONL file."""

    with path.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(
                json.dumps(record, ensure_ascii=False) + "\n"
            )


def main():
    candidates = load_jsonl(CANDIDATES_FILE)
    qrels = load_jsonl(QRELS_FILE)

    # Refuse to merge an incomplete annotation pool.
    #
    # An unanswered candidate must remain unjudged rather than being
    # accidentally converted into a non-relevant judgment.
    unjudged = [
        candidate
        for candidate in candidates
        if candidate["relevance"] is None
    ]

    if unjudged:
        print(
            f"Cannot merge: {len(unjudged)} candidates "
            "are still unjudged."
        )
        return

    # Record every query-document pair that already has a judgment.
    #
    # Existing qrels are authoritative and are never overwritten by this
    # script. This also makes repeated runs safe: previously merged pairs
    # simply get skipped.
    existing_pairs = {
        (qrel["query_id"], qrel["arxiv_id"])
        for qrel in qrels
    }

    new_qrels = []

    for candidate in candidates:
        pair = (
            candidate["query_id"],
            candidate["arxiv_id"],
        )

        # Avoid duplicate judgments for the same query-document pair.
        if pair in existing_pairs:
            continue

        # Only the fields required for evaluation are copied into qrels.
        # Query text, title, and abstract remain in the annotation file.
        new_qrels.append(
            {
                "query_id": candidate["query_id"],
                "arxiv_id": candidate["arxiv_id"],
                "relevance": candidate["relevance"],
            }
        )

    # Preserve all existing judgments and append only genuinely new ones.
    combined_qrels = qrels + new_qrels

    save_jsonl(QRELS_FILE, combined_qrels)

    print(f"Existing judgments: {len(qrels)}")
    print(f"New judgments added: {len(new_qrels)}")
    print(f"Total judgments: {len(combined_qrels)}")


if __name__ == "__main__":
    main()