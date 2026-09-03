import json
from pathlib import Path


CANDIDATES_FILE = Path(
    "data/benchmark_v2/eval/pool_candidates.jsonl"
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

    total = len(candidates)
    completed = sum(
        candidate["relevance"] is not None
        for candidate in candidates
    )

    print(f"Candidates: {total}")
    print(f"Already judged: {completed}")
    print(f"Remaining: {total - completed}")
    print()

    for index, candidate in enumerate(candidates):
        # Ignore candidates that already have a judgment.
        if candidate["relevance"] is not None:
            continue

        print("=" * 80)
        print(
            f"Progress: {completed}/{total}"
        )
        print()
        print(f"Query ID: {candidate['query_id']}")
        print(f"Query: {candidate['query']}")
        print()
        print("Information need:")
        print(candidate["description"])
        print()
        print(f"arXiv: {candidate['arxiv_id']}")
        print(f"Title: {candidate['title']}")
        print()
        print("Abstract:")
        print(candidate["abstract"])
        print()

        while True:
            judgment = input(
                "Relevant? [1 = yes, 0 = no, s = skip, q = quit]: "
            ).strip().lower()

            if judgment == "1":
                candidate["relevance"] = 1
                completed += 1
                save_jsonl(CANDIDATES_FILE, candidates)
                print("Saved: relevant")
                print()
                break

            if judgment == "0":
                candidate["relevance"] = 0
                completed += 1
                save_jsonl(CANDIDATES_FILE, candidates)
                print("Saved: non-relevant")
                print()
                break

            if judgment == "s":
                print("Skipped.")
                print()
                break

            if judgment == "q":
                print()
                print(
                    f"Stopping. Progress saved: "
                    f"{completed}/{total} judged."
                )
                return

            print("Please enter 1, 0, s, or q.")

    print("=" * 80)
    print("All available candidates have been reviewed.")
    print(f"Judged: {completed}/{total}")


if __name__ == "__main__":
    main()
