import csv
from io import StringIO
from typing import List
from models.audit_log import AuditLog


def logs_to_csv(logs: List[AuditLog]) -> str:
    output = StringIO()
    writer = csv.writer(output)
    header = ["id", "user_id", "action", "ip_address", "timestamp", "metadata", "immutable"]
    writer.writerow(header)

    for log in logs:
        writer.writerow(
            [
                log.id,
                log.user_id,
                log.action,
                log.ip_address,
                log.timestamp.isoformat() if log.timestamp else "",
                log.details or "",
                log.immutable,
            ]
        )

    return output.getvalue()


def export_logs_csv(logs: List[AuditLog], file_path: str) -> None:
    csv_str = logs_to_csv(logs)
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        f.write(csv_str)
