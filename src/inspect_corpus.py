import json
from pathlib import Path


# Location of the raw arXiv corpus.
DATA_FILE = Path("data/benchmark_v2/corpus/arxiv_papers.jsonl")

def main():
    papers = []

    # Load all papers from the JSONL corpus.
    # Blank lines are ignored so accidental whitespace does not break parsing.
    with DATA_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                papers.append(json.loads(line))

    # Basic corpus-size check.
    print(f"Number of papers: {len(papers)}")

    # Count papers whose retrieval-relevant text fields are empty.
    # Title and abstract are especially important because retrieval uses
    # their concatenation as the document representation.
    missing_titles = 0
    missing_abstracts = 0

    for paper in papers:
        if not paper["title"].strip():
            missing_titles += 1

        if not paper["abstract"].strip():
            missing_abstracts += 1

    print(f"Papers with missing titles: {missing_titles}")
    print(f"Papers with missing abstracts: {missing_abstracts}")

    # Print a small sample for manual inspection of the corpus contents.
    print("\nFirst five papers:\n")

    for paper in papers[:5]:
        print(paper["arxiv_id"])
        print(paper["title"])
        print(", ".join(paper["authors"]))
        print("-" * 80)


if __name__ == "__main__":
    main()