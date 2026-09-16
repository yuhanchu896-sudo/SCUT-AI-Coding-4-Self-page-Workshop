"""Small, inspectable KNN implementation for the workshop."""
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from math import dist, isfinite
from statistics import fmean, pstdev

from .data import DatasetError, FruitRow, LABELS


@dataclass(frozen=True, slots=True)
class StandardScaler:
    mean: tuple[float, float]
    scale: tuple[float, float]

    @classmethod
    def fit(cls, train: Sequence[FruitRow]) -> "StandardScaler":
        """Learn population mean/std from training rows only; constant std becomes 1."""
        if not train:
            raise DatasetError("训练集不能为空")
        weight = [r.weight_g for r in train]
        diameter = [r.diameter_cm for r in train]
        return cls((fmean(weight), fmean(diameter)), (pstdev(weight) or 1.0, pstdev(diameter) or 1.0))

    def transform(self, weight_g: float, diameter_cm: float) -> tuple[float, float]:
        """Reuse learned statistics; never fit on validation, test, or query values."""
        if not all(isfinite(v) for v in (weight_g, diameter_cm)):
            raise DatasetError("预测输入必须是有限数值")
        return ((weight_g - self.mean[0]) / self.scale[0], (diameter_cm - self.mean[1]) / self.scale[1])


@dataclass(frozen=True, slots=True)
class Neighbor:
    fruit_id: str
    label: str
    distance: float


@dataclass(frozen=True, slots=True)
class KNNClassifier:
    train: tuple[FruitRow, ...]
    scaler: StandardScaler
    k: int

    @classmethod
    def fit(cls, train: Sequence[FruitRow], k: int = 3) -> "KNNClassifier":
        """Store training rows and train-only scaler; k must be a positive integer."""
        if type(k) is not int or not 1 <= k <= len(train):
            raise DatasetError("k 必须是正整数且不超过训练样本数")
        return cls(tuple(train), StandardScaler.fit(train), k)

    def neighbors(self, weight_g: float, diameter_cm: float) -> tuple[Neighbor, ...]:
        """Order by standardized Euclidean distance, then fruit ID for exact ties."""
        query = self.scaler.transform(weight_g, diameter_cm)
        neighbors = (Neighbor(r.fruit_id, r.label, dist(query, self.scaler.transform(r.weight_g, r.diameter_cm))) for r in self.train)
        return tuple(sorted(neighbors, key=lambda n: (n.distance, n.fruit_id))[:self.k])

    def predict(self, weight_g: float, diameter_cm: float) -> str:
        """Vote; tied counts choose smaller summed distance, then label alphabetically."""
        neighbors = self.neighbors(weight_g, diameter_cm)
        counts = Counter(n.label for n in neighbors)
        return min(counts, key=lambda label: (-counts[label], sum(n.distance for n in neighbors if n.label == label), label))


@dataclass(frozen=True, slots=True)
class Evaluation:
    accuracy: float
    labels: tuple[str, ...]
    confusion: tuple[tuple[int, ...], ...]
    predictions: tuple[str, ...]


def evaluate(classifier: KNNClassifier, rows: Sequence[FruitRow]) -> Evaluation:
    """Confusion rows are true labels; columns are predicted labels, in labels order."""
    if not rows:
        raise DatasetError("评估集不能为空")
    predictions = tuple(classifier.predict(r.weight_g, r.diameter_cm) for r in rows)
    confusion = tuple(tuple(sum(r.label == actual and p == predicted for r, p in zip(rows, predictions)) for predicted in LABELS) for actual in LABELS)
    return Evaluation(sum(r.label == p for r, p in zip(rows, predictions)) / len(rows), LABELS, confusion, predictions)


@dataclass(frozen=True, slots=True)
class ValidationScore:
    k: int
    accuracy: float


@dataclass(frozen=True, slots=True)
class Selection:
    k: int
    scores: tuple[ValidationScore, ...]


def select_k(train: Sequence[FruitRow], validation: Sequence[FruitRow], candidates: Sequence[int] = (1, 3, 5)) -> Selection:
    """Choose using validation accuracy only; equal accuracy prefers smaller k."""
    if not candidates:
        raise DatasetError("至少提供一个候选 k")
    scores = tuple(ValidationScore(k, evaluate(KNNClassifier.fit(train, k), validation).accuracy) for k in candidates)
    best = min(scores, key=lambda score: (-score.accuracy, score.k))
    return Selection(best.k, scores)


def majority_baseline(train: Sequence[FruitRow], test: Sequence[FruitRow]) -> float:
    """Always predict training-set majority (alphabetical ties), then score on test."""
    if not train or not test:
        raise DatasetError("训练集和测试集不能为空")
    counts = Counter(row.label for row in train)
    majority = min(counts, key=lambda label: (-counts[label], label))
    return sum(row.label == majority for row in test) / len(test)
