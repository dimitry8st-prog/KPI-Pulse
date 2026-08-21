import csv
import sqlite3

from src.interaction_logger import Interaction, InteractionLogger, anonymize_user_id


def test_log_stats_and_anonymization(tmp_path):
    db_path = tmp_path / "logs.db"
    logger = InteractionLogger(str(db_path))
    logger.log(Interaction(
        source="telegram", event_type="command_digest", request="/digest",
        response="done", user_id="123456", duration_ms=120,
    ))
    logger.log(Interaction(
        source="streamlit", event_type="ai_question", status="error",
        request="question", error="timeout", duration_ms=80,
    ))

    stats = logger.get_stats()
    assert stats == {
        "total": 2, "successful": 1, "failed": 1,
        "error_rate": 50.0, "avg_duration_ms": 100.0,
    }
    with sqlite3.connect(db_path) as conn:
        stored_id = conn.execute(
            "SELECT user_id_hash FROM interaction_logs WHERE source='telegram'"
        ).fetchone()[0]
    assert stored_id == anonymize_user_id("123456")
    assert stored_id != "123456"


def test_secrets_are_redacted_and_csv_is_exported(tmp_path):
    logger = InteractionLogger(str(tmp_path / "logs.db"))
    logger.log(Interaction(
        source="streamlit", event_type="ai_question",
        request="api_key=super-secret-value",
        response="token: another-secret-value",
    ))
    output = tmp_path / "export.csv"
    logger.export_csv(str(output))

    with output.open(encoding="utf-8-sig") as handle:
        row = next(csv.DictReader(handle))
    assert "super-secret-value" not in row["request"]
    assert "another-secret-value" not in row["response"]
    assert "[REDACTED]" in row["request"]
