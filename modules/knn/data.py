"""CSV boundary and reproducible fruit dataset partitions (standard library only)."""
from collections import Counter
from collections.abc import Sequence
import csv
from dataclasses import dataclass
from decimal import Decimal
from math import isfinite
from pathlib import Path
from random import Random
import re
from typing import Final

LABELS: Final = ("apple", "orange", "pear")
HEADER: Final = ("fruit_id", "weight_g", "diameter_cm", "label")


@dataclass(frozen=True, slots=True)
class DatasetError(ValueError):
    message: str

    def __str__(self) -> str:
        return self.message


@dataclass(frozen=True, slots=True)
class FruitRow:
    fruit_id: str
    weight_g: float
    diameter_cm: float
    label: str


@dataclass(frozen=True, slots=True)
class RawRow:
    line: int
    values: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class AuditRecord:
    line: int
    fruit_id: str
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class CleaningResult:
    rows: tuple[FruitRow, ...]
    audit: tuple[AuditRecord, ...]


@dataclass(frozen=True, slots=True)
class DatasetSplit:
    train: tuple[FruitRow, ...]
    validation: tuple[FruitRow, ...]
    test: tuple[FruitRow, ...]


def read_csv(path: str | Path) -> tuple[RawRow, ...]:
    """Read UTF-8 CSV, preserving physical line numbers for the audit."""
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream)
        if tuple(next(reader, [])) != HEADER:
            raise DatasetError("CSV 表头必须为 " + ",".join(HEADER))
        rows: list[RawRow] = []
        for values in reader:
            rows.append(RawRow(reader.line_num, tuple(values)))
        return tuple(rows)


def _number(raw: str, field: str) -> tuple[float | None, str]:
    text = raw.strip().lower()
    if not text:
        return None, "missing"
    try:
        value = float(text)
    except ValueError:
        found = re.fullmatch(r"([+-]?(?:\d+(?:\.\d*)?|\.\d+))\s*([a-z]+)", text)
        if found is None:
            return None, "invalid_number"
        units = {"g": "1", "kg": "1000"} if field == "weight_g" else {"cm": "1", "mm": "0.1"}
        if found[2] not in units:
            return None, "unit"
        value = float(Decimal(found[1]) * Decimal(units[found[2]]))
    if not isfinite(value):
        return None, "nonfinite"
    lower, upper = (50, 500) if field == "weight_g" else (3, 15)
    if not lower <= value <= upper:
        return None, "range"
    return value, ""


def clean_rows(raw_rows: Sequence[RawRow]) -> CleaningResult:
    """Normalize explicit units; remove repeats; quarantine every conflicting ID.

    Ranges (50–500 g, 3–15 cm) are classroom collection rules, not universal
    biological limits. Missing or suspicious measurements are never guessed.
    """
    audit: list[AuditRecord] = []
    candidates: list[tuple[RawRow, FruitRow]] = []
    signatures: dict[str, set[tuple[str, ...]]] = {}
    malformed_ids: set[str] = set()
    for raw in raw_rows:
        values = tuple(value.strip() for value in raw.values)
        fruit_id = values[0] if values else ""
        if len(values) != 4:
            if fruit_id:
                malformed_ids.add(fruit_id)
            audit.append(AuditRecord(raw.line, fruit_id, "columns", "列数不是 4，隔离此行"))
            continue
        weight, wc = _number(values[1], "weight_g")
        diameter, dc = _number(values[2], "diameter_cm")
        label = values[3].lower()
        signature = (str(weight) if weight is not None else values[1], str(diameter) if diameter is not None else values[2], label)
        if fruit_id:
            signatures.setdefault(fruit_id, set()).add(signature)
        issues = (["missing"] if not fruit_id else []) + (["label"] if label not in LABELS else [])
        issues += [code for code in (wc, dc) if code]
        if issues:
            for code in issues:
                audit.append(AuditRecord(raw.line, fruit_id, code, "字段不符合采集规则，隔离此行"))
            continue
        if weight is not None and diameter is not None:
            row = FruitRow(fruit_id, weight, diameter, label)
            candidates.append((raw, row))
            if raw.values != (fruit_id, str(weight), str(diameter), label):
                audit.append(AuditRecord(raw.line, fruit_id, "normalized", "空白、标签大小写或数值/显式单位已标准化"))
    conflicts = {key for key, values in signatures.items() if len(values) > 1} | malformed_ids
    clean: list[FruitRow] = []
    seen: set[str] = set()
    for raw, row in candidates:
        if row.fruit_id in conflicts:
            audit.append(AuditRecord(raw.line, row.fruit_id, "conflicting_id", "同一 ID 的记录冲突，全部隔离"))
        elif row.fruit_id in seen:
            audit.append(AuditRecord(raw.line, row.fruit_id, "duplicate_id", "同一 ID 的完全重复记录，仅保留一条"))
        else:
            seen.add(row.fruit_id)
            clean.append(row)
    return CleaningResult(tuple(clean), tuple(audit))


def write_clean_csv(path: str | Path, rows: Sequence[FruitRow]) -> None:
    """Export cleaned measurements in grams and centimetres."""
    with Path(path).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(HEADER)
        writer.writerows((r.fruit_id, r.weight_g, r.diameter_cm, r.label) for r in rows)


def stratified_split(rows: Sequence[FruitRow], seed: int = 42) -> DatasetSplit:
    """Split each class roughly 60/20/20 after stable ID sorting, without leakage."""
    counts = Counter(row.fruit_id for row in rows)
    if any(count > 1 for count in counts.values()):
        raise DatasetError("请先清洗重复 fruit_id，再划分数据")
    rng = Random(seed)
    train: list[FruitRow] = []
    validation: list[FruitRow] = []
    test: list[FruitRow] = []
    if any(row.label not in LABELS for row in rows):
        raise DatasetError("标签只支持 apple、orange、pear")
    for label in LABELS:
        group = sorted((row for row in rows if row.label == label), key=lambda row: row.fruit_id)
        if len(group) < 5:
            raise DatasetError(f"{label} 至少 5 个独立水果才能划分三份；建议每类 20 个以上")
        rng.shuffle(group)
        heldout = max(1, round(len(group) * 0.2))
        train.extend(group[: -2 * heldout])
        validation.extend(group[-2 * heldout : -heldout])
        test.extend(group[-heldout:])
    return DatasetSplit(tuple(train), tuple(validation), tuple(test))
