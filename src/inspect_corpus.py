import json
from pathlib import Path


DATA_FILE = Path("data/raw/arxiv_papers.jsonl")


def main():
    papers = []

    with DATA_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            papers.append(json.loads(line))

    print(f"Number of papers: {len(papers)}")

    print("\nFirst five papers:\n")

    for paper in papers[:5]:
        print(paper["arxiv_id"])
        print(paper["title"])
        print(", ".join(paper["authors"]))
        print("-" * 80)


if __name__ == "__main__":
    main()

