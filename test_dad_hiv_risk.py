import pytest
from dad_hiv_risk import calculate_metrics, process_batch


def test_dad_hiv_risk_single():
    res = calculate_metrics(v1=12.0, v2=4.0)
    assert "score" in res
    assert "classification" in res
    assert res["score"] > 0


def test_dad_hiv_risk_batch(tmp_path):
    csv_in = tmp_path / "in.csv"
    csv_out = tmp_path / "out.csv"
    csv_in.write_text("Patient,v1,v2\nPat_001,15.0,3.0\nPat_002,5.0,1.0\n", encoding="utf-8")

    process_batch(str(csv_in), str(csv_out))
    assert csv_out.exists()
    content = csv_out.read_text(encoding="utf-8")
    assert "Pat_001" in content
    assert "score" in content


def test_calculate_metrics_no_args():
    """Test calculate_metrics with no arguments returns default score."""
    res = calculate_metrics()
    assert "score" in res
    assert "classification" in res
    assert res["inputs_evaluated"] == 0


def test_calculate_metrics_string_only():
    """Test calculate_metrics with only string values."""
    res = calculate_metrics(name="test", label="abc")
    assert "score" in res
    assert res["inputs_evaluated"] == 2


def test_calculate_metrics_mixed_types():
    """Test calculate_metrics with mixed numeric and string values."""
    res = calculate_metrics(v1=10.0, v2="text", v3=5.5)
    assert res["score"] > 0
    assert res["inputs_evaluated"] == 3


def test_calculate_metrics_classification_tiers():
    """Test classification tiers based on score thresholds."""
    low = calculate_metrics(v1=5.0)
    assert low["classification"] == "Low / Standard"

    moderate = calculate_metrics(v1=15.0)
    assert moderate["classification"] == "Moderate / Intermediate"

    high = calculate_metrics(v1=30.0)
    assert high["classification"] == "High / Severe"


def test_process_batch_file_not_found(tmp_path):
    """Test process_batch raises FileNotFoundError for missing input."""
    csv_out = tmp_path / "out.csv"
    with pytest.raises(FileNotFoundError):
        process_batch(str(tmp_path / "nonexistent.csv"), str(csv_out))


def test_process_batch_empty_csv(tmp_path):
    """Test process_batch raises ValueError for empty CSV."""
    csv_in = tmp_path / "empty.csv"
    csv_out = tmp_path / "out.csv"
    csv_in.write_text("", encoding="utf-8")
    with pytest.raises(ValueError):
        process_batch(str(csv_in), str(csv_out))


def test_process_batch_creates_output_directory(tmp_path):
    """Test process_batch creates output directory if it doesn't exist."""
    csv_in = tmp_path / "in.csv"
    csv_out = tmp_path / "subdir" / "nested" / "out.csv"
    csv_in.write_text("Patient,v1\nPat_001,10.0\n", encoding="utf-8")
    process_batch(str(csv_in), str(csv_out))
    assert csv_out.exists()
