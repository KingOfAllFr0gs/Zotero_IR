import json
from pathlib import Path


CANDIDATES_FILE = Path(
    "data/benchmark_v2/eval/pool_candidates.jsonl"
)

QRELS_FILE = Path(
    "data/benchmark_v2/eval/qrels.jsonl"
)


def load_jsonl(path):
    records = []

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                records.append(json.loads(line))

    return records


def save_jsonl(path, records):
    with path.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(
                json.dumps(record, ensure_ascii=False) + "\n"
            )


def main():
    candidates = load_jsonl(CANDIDATES_FILE)
    qrels = load_jsonl(QRELS_FILE)

    # Refuse to merge an incomplete annotation pool.
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

    # Existing query-document pairs are kept unchanged.
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

        if pair in existing_pairs:
            continue

        new_qrels.append(
            {
                "query_id": candidate["query_id"],
                "arxiv_id": candidate["arxiv_id"],
                "relevance": candidate["relevance"],
            }
        )

    combined_qrels = qrels + new_qrels

    save_jsonl(QRELS_FILE, combined_qrels)

    print(f"Existing judgments: {len(qrels)}")
    print(f"New judgments added: {len(new_qrels)}")
    print(f"Total judgments: {len(combined_qrels)}")


if __name__ == "__main__":
    main()
