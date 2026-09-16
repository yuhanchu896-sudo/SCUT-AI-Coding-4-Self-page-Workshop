#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
# ─── How to run ───
# From the project root: python -m modules.knn.build_notebook
# Or, with uv installed: uv run -m modules.knn.build_notebook
"""Build the student notebook from the adjacent readable lesson source."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TypedDict


class Cell(TypedDict, total=False):
    cell_type: str
    id: str
    metadata: dict[str, str]
    source: list[str]
    execution_count: None
    outputs: list[str]


def main() -> None:
    """Translate Python fences into executable cells, retaining all lesson text."""
    folder = Path(__file__).resolve().parent
    cells: list[Cell] = []
    text = (folder / "lesson.md").read_text(encoding="utf-8")
    for index, chunk in enumerate(text.split("```python\n")):
        if index:
            code, chunk = chunk.split("```", 1)
            cells.append(Cell(cell_type="code", id=f"code-{index}", metadata={},
                              source=code.splitlines(keepends=True), execution_count=None,
                              outputs=[]))
        if chunk.strip():
            cells.append(Cell(cell_type="markdown", id=f"text-{index}", metadata={},
                              source=chunk.strip().splitlines(keepends=True)))
    notebook = {
        "cells": cells,
        "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python",
                                    "name": "python3"},
                     "language_info": {"name": "python", "version": "3.10"}},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    target = folder.parents[1] / "KNN_Workshop_Student.ipynb"
    target.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Generated {target.name}: {len(cells)} cells")


if __name__ == "__main__":
    main()
