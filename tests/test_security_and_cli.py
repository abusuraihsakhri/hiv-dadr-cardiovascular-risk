"""Security and CLI regression tests."""
import csv

from agents.base import AuditTrail
from agents.models import SystemTaskPayload
from cli import main


def test_audit_hmac_detects_modified_fields():
    trail = AuditTrail(secret_key="test-only-key")
    trail.log("tester", "reviewer", "EVENT", {"status": "OK"})
    assert trail.verify_integrity()
    trail.logs[0]["event_type"] = "FORGED"
    assert not trail.verify_integrity()


def test_audit_hmac_detects_signature_change():
    trail = AuditTrail(secret_key="test-only-key")
    trail.log("tester", "reviewer", "EVENT", {"status": "OK"})
    trail.logs[0]["current_hash"] = "0" * 64
    assert not trail.verify_integrity()


def test_audit_chain_detects_prev_hash_change():
    trail = AuditTrail(secret_key="test-only-key")
    trail.log("tester", "reviewer", "FIRST", {"count": 1})
    trail.log("tester", "reviewer", "SECOND", {"count": 2})
    trail.logs[1]["prev_hash"] = "forged"
    assert not trail.verify_integrity()


def test_returned_audit_log_is_copy():
    trail = AuditTrail(secret_key="test-only-key")
    trail.log("tester", "reviewer", "EVENT", {"status": "OK"})
    entries = trail.get_trail()
    entries[0]["event_type"] = "changed"
    entries.clear()
    assert len(trail.get_trail()) == 1
    assert trail.verify_integrity()


def test_non_finite_metrics_rejected():
    import pytest
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        SystemTaskPayload(task_id="test", target_identifier="key", primary_metric=float("nan"))


def test_batch_false_flag_does_not_trigger_critical(tmp_path):
    source = tmp_path / "in.csv"
    dest = tmp_path / "out.csv"
    source.write_text(
        "task_id,target_identifier,primary_metric,secondary_metric,status_descriptor,is_critical_flag\n"
        "TEST-01,KEY-01,1.0,1.0,NOMINAL,False\n"
        "TEST-02,KEY-02,1.0,1.0,NOMINAL,True\n", encoding="utf-8"
    )
    assert main(["batch", "-i", str(source), "-o", str(dest)]) == 0
    with dest.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    assert rows[0]["overall_urgency"] == "ROUTINE"
    assert rows[1]["overall_urgency"] == "CRITICAL_STAT_PANIC"
