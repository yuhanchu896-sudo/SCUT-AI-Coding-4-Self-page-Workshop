# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
# How to run: python -m modules.knn.generate_data (from repository root)
"""Generate simulated classroom measurements, NOT real fruit observations.

Seed 2026; 24 examples per class with deliberately overlapping distributions.
These measurements illustrate workflow and cannot establish real-world accuracy.
"""
import csv
from pathlib import Path
from random import Random

from .data import HEADER


def generate_data(directory: Path) -> None:
    """Write 72 simulated fruits plus ten dirty/repeated input rows."""
    rng = Random(2026)
    records: list[tuple[str, str, str, str]] = []
    for label, weight, diameter in (("apple", 170, 7.6), ("orange", 205, 7.0), ("pear", 145, 6.2)):
        for index in range(24):
            records.append((f"{label[0].upper()}{index + 1:03}", f"{rng.gauss(weight, 22):.1f}", f"{rng.gauss(diameter, 0.45):.2f}", label))
    records.extend([
        records[0],
        ("D001", "", "7", "apple"),
        ("D002", "heavy", "7", "orange"),
        ("D003", "NaN", "7", "pear"),
        ("D004", "1800", "7", "apple"),
        ("D005", "180 lb", "7", "orange"),
        ("D006", "180", "7", "banana"),
        ("D007", "180", "7", "apple"),
        ("D007", "180", "7", "pear"),
        ("D008", "180", "7", "apple"),
        ("D008", "180", "7", "pear"),
        (records[1][0], f"{float(records[1][1]) / 1000:g} kg", records[1][2], " APPLE "),
    ])
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / "fruits_raw.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(HEADER)
        writer.writerows(records)
    with (directory / "collection_template.csv").open("w", encoding="utf-8", newline="") as stream:
        csv.writer(stream).writerow(HEADER)


if __name__ == "__main__":
    generate_data(Path(__file__).parent / "data")
