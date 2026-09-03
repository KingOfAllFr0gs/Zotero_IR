import json
import re
from pathlib import Path

import arxiv

# Existing v2 corpus, initially seeded with the 104 pilot papers.
INPUT_FILE = Path("data/benchmark_v2/corpus/arxiv_papers.jsonl")

# Write to a new file first so that corpus expansion cannot accidentally
# destroy the current benchmark corpus.
OUTPUT_FILE = Path(
    "data/benchmark_v2/corpus/arxiv_papers_expanded.jsonl"
)

# Broad discovery queries covering the mathematical region of the
# expanded benchmark. These are intentionally broader than the individual
# evaluation queries.
QUERIES = [
    'all:"geometric analysis"',
    'all:"calculus of variations"',
    'all:"critical point theory"',
    'all:"geometric measure theory"',
    'all:"concentration compactness"',
    'all:"Morse theory"',
    'all:"harmonic maps"',
    'all:"minimal surfaces"',
    'all:"isoperimetric problem"',
    'all:"Sobolev inequalities"',
    'all:"free boundary"',
    'all:"geometric flow"',
    'all:"Gamma convergence"',
    'all:"spectral geometry"',
    'all:"nonlinear elliptic equations"',
]

RESULTS_PER_QUERY = 40

def base_arxiv_id(arxiv_id):
    """Remove the version suffix from an arXiv ID."""

    return re.sub(r"v\d+$", "", arxiv_id)

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
    # Start with all papers already present in benchmark v2.
    # This preserves the exact pilot records and their versioned arXiv IDs,
    # which is important because existing qrels refer to those IDs.
    with INPUT_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                paper = json.loads(line)
                papers[base_arxiv_id(paper["arxiv_id"])] = paper

    print(f"Starting with {len(papers)} existing papers.")

    for query in QUERIES:
        print(f"\nSearching for: {query}")

        search = arxiv.Search(
            query=query,
            max_results=RESULTS_PER_QUERY,
            sort_by=arxiv.SortCriterion.Relevance,
        )

        for result in client.results(search):
            paper = paper_to_dict(result)

            base_id = base_arxiv_id(paper["arxiv_id"])

            # Keep an existing paper if the same underlying arXiv paper is already
            # present. In particular, this prevents newer arXiv versions from replacing
            # pilot papers that already have relevance judgments.
            if base_id not in papers:
                papers[base_id] = paper

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
