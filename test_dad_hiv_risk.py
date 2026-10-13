"""Regression tests: no unvalidated HIV cardiovascular risk prediction."""
import csv
import json

import pytest

from dad_hiv_risk import calculate_metrics, main, process_batch

VALID = dict(
    age=48, sex="male", systolic_bp=130, smoking_status="former",
    family_history_cvd="no", diabetes="no",
    total_cholesterol=5.2, hdl_cholesterol=1.3, cd4_count=650,
)


def test_complete_inputs_do_not_generate_risk_or_treatment():
    result = calculate_metrics(**VALID)
    assert result["status"] == "INPUTS_COMPLETE"
    assert result["score"] is None
    assert result["risk_5y_percent"] is None
    assert result["classification"] == "NOT_CALCULATED"
    assert result["clinical_recommendation"] == "No clinical recommendation is calculated."
    assert result["missing_inputs"] == []
    assert result["validation_errors"] == []


def test_missing_predictors_are_reported():
    result = calculate_metrics(age=45)
    assert result["status"] == "INPUTS_INCOMPLETE"
    assert "cd4_count" in result["missing_inputs"]
    assert result["risk_5y_percent"] is None


@pytest.mark.parametrize("override", [
    {"age": "nan"}, {"age": float("inf")}, {"age": True},
    {"sex": "invalid"}, {"smoking_status": "unknown"},
    {"systolic_bp": -20}, {"cd4_count": 0},
    {"diabetes": "maybe"}, {"family_history_cvd": "maybe"},
    {"hdl_cholesterol": 8},  # exceeds total cholesterol
    {"unexpected": "value"},
])
def test_bad_inputs_cannot_be_marked_complete(override):
    result = calculate_metrics(**(VALID | override))
    assert result["status"] == "INPUTS_INCOMPLETE"
    assert result["validation_errors"]
    assert result["score"] is None


def test_invalid_numeric_string_cannot_raise_conversion_exception():
    result = calculate_metrics(**(VALID | {"total_cholesterol": "not a number"}))
    assert result["status"] == "INPUTS_INCOMPLETE"


def test_no_input_is_not_default_risk_estimate():
    result = calculate_metrics()
    assert result["score"] is None
    assert len(result["missing_inputs"]) == 9


def test_cli_single_outputs_non_scored_json(capsys):
    args = ["single"]
    for key, value in VALID.items():
        args += ["--" + key.replace("_", "-"), str(value)]
    assert main(args) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "INPUTS_COMPLETE"
    assert result["score"] is None


def test_batch_preserves_rows_and_replaces_stale_risk(tmp_path):
    source = tmp_path / "cohort.csv"
    output = tmp_path / "nested" / "validated.csv"
    fields = ["subject"] + list(VALID) + ["risk_5y_percent"]
    with source.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerow({"subject": "study-001", **VALID, "risk_5y_percent": "99"})
    process_batch(str(source), str(output))
    with output.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        rows = list(reader)
        assert len(reader.fieldnames) == len(set(reader.fieldnames))
    assert rows[0]["subject"] == "study-001"
    assert rows[0]["risk_5y_percent"] == ""
    assert rows[0]["validation_status"] == "INPUTS_COMPLETE"


def test_batch_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        process_batch(str(tmp_path / "missing.csv"), str(tmp_path / "out.csv"))


def test_batch_rejects_missing_and_duplicate_headers(tmp_path):
    for data in ("", "age,age\n40,41\n"):
        source = tmp_path / "bad.csv"
        source.write_text(data, encoding="utf-8")
        with pytest.raises(ValueError):
            process_batch(str(source), str(tmp_path / "out.csv"))


def test_batch_rejects_extra_columns(tmp_path):
    source = tmp_path / "bad.csv"
    source.write_text("age,sex\n40,male,extra\n", encoding="utf-8")
    with pytest.raises(ValueError):
        process_batch(str(source), str(tmp_path / "out.csv"))


def test_batch_rejects_overwrite(tmp_path):
    source = tmp_path / "same.csv"
    source.write_text("age\n45\n", encoding="utf-8")
    with pytest.raises(ValueError):
        process_batch(str(source), str(source))
