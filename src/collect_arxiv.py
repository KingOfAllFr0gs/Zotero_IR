import json
from pathlib import Path

import arxiv


OUTPUT_FILE = Path("data/raw/arxiv_papers.jsonl")

QUERIES = [
    'all:"geometric knot theory"',
    'all:"calculus of variations"',
    'all:"Palais-Smale"',
    'all:"gradient flow"',
    'all:"knot energy"',
]

RESULTS_PER_QUERY = 25


def paper_to_dict(paper):
    """Convert an arXiv result into a simple Python dictionary."""

    return {
        "arxiv_id": paper.get_short_id(),
        "title": paper.title.strip(),
        "abstract": paper.summary.strip(),
        "authors": [author.name for author in paper.authors],
        "published": paper.published.isoformat(),
        "updated": paper.updated.isoformat(),
        "categories": paper.categories,
        "pdf_url": paper.pdf_url,
        "entry_url": paper.entry_id,
    }


def main():
    client = arxiv.Client(
        page_size=50,
        delay_seconds=3.0,
        num_retries=3,
    )

    papers = {}

    for query in QUERIES:
        print(f"\nSearching for: {query}")

        search = arxiv.Search(
            query=query,
            max_results=RESULTS_PER_QUERY,
            sort_by=arxiv.SortCriterion.Relevance,
        )

        for result in client.results(search):
            paper = paper_to_dict(result)

            # Using the arXiv ID as the dictionary key automatically
            # removes duplicate papers returned by several queries.
            papers[paper["arxiv_id"]] = paper

        print(f"Corpus currently contains {len(papers)} unique papers.")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        for paper in papers.values():
            file.write(json.dumps(paper, ensure_ascii=False) + "\n")

    print()
    print(f"Finished!")
    print(f"Saved {len(papers)} papers to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
