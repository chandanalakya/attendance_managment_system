import csv
import io
from typing import List, Dict, Any

# ✅ Correct import path (fixed)
from src.models.audit_log import AuditLog


def logs_to_csv(logs: List[Dict[str, Any]]) -> str:
    """
    Converts a list of log dictionaries or ORM objects into a CSV string.
    Works with both AuditLog ORM instances and plain dictionaries.
    """
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        ["id", "user_id", "action", "ip_address", "timestamp", "metadata", "immutable"]
    )

    for log in logs:
        # Handles either dicts or objects
        if isinstance(log, dict):
            row = [
                log.get("id"),
                log.get("user_id"),
                log.get("action"),
                log.get("ip_address"),
                log.get("timestamp"),
                log.get("metadata"),
                log.get("immutable"),
            ]
        else:
            row = [
                getattr(log, "id", None),
                getattr(log, "user_id", None),
                getattr(log, "action", None),
                getattr(log, "ip_address", None),
                getattr(log, "timestamp", None),
                getattr(log, "metadata", None),
                getattr(log, "immutable", None),
            ]
        writer.writerow(row)

    return output.getvalue()


def export_logs_csv(logs: List[Dict[str, Any]], file_path: str) -> None:
    """
    Writes the CSV data to a specified file.
    """
    csv_content = logs_to_csv(logs)
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        f.write(csv_content)
