from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


OUTPUT_FILE = Path("docs/assets/precision_at_5_by_query.png")

QUERY_IDS = [f"q{i:03d}" for i in range(1, 21)]

BM25_P5 = [
    0.6, 0.2, 0.8, 1.0, 0.0,
    0.4, 0.2, 1.0, 0.0, 0.6,
    1.0, 0.0, 0.2, 0.6, 0.6,
    0.6, 0.6, 1.0, 0.6, 0.4,
]

DENSE_P5 = [
    0.8, 0.2, 0.8, 1.0, 0.6,
    0.6, 0.0, 1.0, 0.0, 1.0,
    1.0, 0.6, 0.6, 0.4, 1.0,
    0.6, 1.0, 1.0, 0.4, 0.6,
]


def main():
    """Plot query-level Precision@5 for the two retrieval baselines."""

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    y = np.arange(len(QUERY_IDS))
    bar_height = 0.38

    fig, ax = plt.subplots(figsize=(9, 8))

    ax.barh(y - bar_height / 2, BM25_P5, bar_height, label="BM25")
    ax.barh(y + bar_height / 2, DENSE_P5, bar_height, label="Dense")

    ax.set_yticks(y)
    ax.set_yticklabels(QUERY_IDS)
    ax.invert_yaxis()

    ax.set_xlim(0, 1)
    ax.set_xlabel("Precision@5")
    ax.set_title("BM25 vs Dense Retrieval by Query")

    ax.legend()

    fig.tight_layout()
    fig.savefig(OUTPUT_FILE, dpi=200)
    plt.close(fig)

    print(f"Saved plot to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()