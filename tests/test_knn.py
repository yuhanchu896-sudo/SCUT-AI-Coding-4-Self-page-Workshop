from pathlib import Path

import pytest

from modules.knn import data, model


def test_cleaning_when_equivalent_decimal_units_share_id() -> None:
    # Given
    rows = (data.RawRow(2, ("a", "180", "6.8", "apple")), data.RawRow(3, ("a", "0.18 kg", "68 mm", "apple")))
    # When
    result = data.clean_rows(rows)
    # Then
    assert result.rows == (data.FruitRow("a", 180, 6.8, "apple"),)
    assert "duplicate_id" in {record.code for record in result.audit}


def test_cleaning_when_measurements_actually_differ() -> None:
    # Given
    rows = (data.RawRow(2, ("a", "180", "6.8", "apple")), data.RawRow(3, ("a", "180", "68.01 mm", "apple")))
    # When
    result = data.clean_rows(rows)
    # Then
    assert result.rows == ()
    assert sum(record.code == "conflicting_id" for record in result.audit) == 2


def test_cleaning_when_malformed_row_reuses_id() -> None:
    # Given
    rows = (data.RawRow(2, ("a", "180", "6.8", "apple")), data.RawRow(3, ("a", "190", "6.8", "pear", "extra")))
    # When
    result = data.clean_rows(rows)
    # Then
    assert result.rows == ()
    assert {record.code for record in result.audit} >= {"columns", "conflicting_id"}


def test_cleaning_when_units_and_bad_rows(tmp_path: Path) -> None:
    # Given
    source = tmp_path / "fruit.csv"
    source.write_text("fruit_id,weight_g,diameter_cm,label\na,0.18 kg,70 mm, Apple \nb,NaN,7,apple\nc,,7,apple\nd,abc,7,pear\ne,2,7,orange\nf,180,7,banana\ng,180 lb,7,apple\nh,180,7,apple\nh,180,7,pear\ni,180,7,apple\ni,180,7,apple\n", encoding="utf-8")
    # When
    result = data.clean_rows(data.read_csv(source))
    # Then
    assert [(r.fruit_id, r.weight_g, r.diameter_cm, r.label) for r in result.rows] == [("a", 180, 7, "apple"), ("i", 180, 7, "apple")]
    assert {a.code for a in result.audit} >= {"normalized", "nonfinite", "missing", "invalid_number", "range", "label", "unit", "conflicting_id", "duplicate_id"}


def test_split_when_balanced_is_disjoint_and_reproducible() -> None:
    # Given
    rows = tuple(data.FruitRow(f"{label}{i}", 100 + i, 5 + i / 10, label) for label in data.LABELS for i in range(10))
    # When
    split = data.stratified_split(rows)
    # Then
    assert split == data.stratified_split(tuple(reversed(rows)))
    assert (len(split.train), len(split.validation), len(split.test)) == (18, 6, 6)
    assert len({r.fruit_id for part in (split.train, split.validation, split.test) for r in part}) == 30


def test_split_when_class_too_small() -> None:
    # Given
    rows = (data.FruitRow("a", 100, 5, "apple"),)
    # When / Then
    with pytest.raises(data.DatasetError, match="至少 5"):
        data.stratified_split(rows)


def test_scaler_when_training_only_and_constant_feature() -> None:
    # Given
    train = (data.FruitRow("a", 100, 5, "apple"), data.FruitRow("b", 200, 5, "pear"))
    # When
    scaler = model.StandardScaler.fit(train)
    # Then
    assert scaler.transform(150, 5) == (0, 0)
    assert scaler.transform(300, 6) == (3, 1)
    assert scaler.mean == (150, 5)


def test_neighbors_when_tied_are_stable() -> None:
    # Given
    rows = (data.FruitRow("b", 200, 7, "pear"), data.FruitRow("a", 100, 7, "apple"))
    # When
    classifier = model.KNNClassifier.fit(rows, k=2)
    # Then
    assert classifier.predict(150, 7) == "apple"
    assert [n.fruit_id for n in classifier.neighbors(150, 7)] == ["a", "b"]
    assert model.KNNClassifier.fit(rows, k=1).predict(199, 7) == "pear"


@pytest.mark.parametrize("k", [0, -1, 3, True, 1.5])
def test_knn_when_invalid_k(k: int) -> None:
    # Given
    rows = (data.FruitRow("a", 100, 5, "apple"), data.FruitRow("b", 200, 7, "pear"))
    # When / Then
    with pytest.raises(data.DatasetError, match="k"):
        model.KNNClassifier.fit(rows, k=k)


def test_pipeline_when_using_bundled_csv(tmp_path: Path) -> None:
    # Given
    source = Path(__file__).parents[1] / "modules/knn/data/fruits_raw.csv"
    # When
    cleaned = data.clean_rows(data.read_csv(source))
    split = data.stratified_split(cleaned.rows)
    selection = model.select_k(split.train, split.validation)
    result = model.evaluate(model.KNNClassifier.fit(split.train, selection.k), split.test)
    target = tmp_path / "clean.csv"
    data.write_clean_csv(target, cleaned.rows)
    # Then
    assert len(cleaned.rows) == 72
    assert 0.5 <= result.accuracy < 1
    assert sum(sum(row) for row in result.confusion) == len(split.test)
    assert result.accuracy > model.majority_baseline(split.train, split.test)
    assert data.clean_rows(data.read_csv(target)).rows == cleaned.rows
