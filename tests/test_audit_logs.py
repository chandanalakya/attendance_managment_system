import csv
import io
from src.models.audit_log import AuditLog
from src.utils.export_csv import logs_to_csv, export_logs_csv
from src.utils.export_pdf import export_logs_pdf


# ---------------------------------------------------------------------
# Helper: create dummy log objects for CSV/PDF export tests
# ---------------------------------------------------------------------

def _create_dummy_logs(count=3):
    logs = []
    for i in range(count):
        # Creating dummy objects as dictionaries, not ORM instances
        log = {
            "id": i + 1,
            "user_id": 100 + i,
            "action": f"action_{i}",
            "ip_address": f"192.168.0.{i}",
            "timestamp": None,
            "metadata": f"meta_{i}",
            "immutable": 1,
        }
        logs.append(log)
    return logs


# ---------------------------------------------------------------------
# TEST: CSV export to string
# ---------------------------------------------------------------------

def test_logs_to_csv_contains_header_and_data(tmp_path):
    logs = _create_dummy_logs(2)
    csv_output = logs_to_csv(logs)

    # Check header row
    lines = csv_output.splitlines()
    assert lines[0].startswith(
        "id,user_id,action,ip_address,timestamp,metadata,immutable"
    )

    # Check data rows
    reader = csv.reader(io.StringIO(csv_output))
    rows = list(reader)
    assert len(rows) == 3
    assert rows[1][1] == "100" and rows[2][1] == "101"


# ---------------------------------------------------------------------
# TEST: CSV export writes file correctly
# ---------------------------------------------------------------------

def test_export_logs_csv_writes_file(tmp_path):
    logs = _create_dummy_logs(1)
    file_path = tmp_path / "logs.csv"
    export_logs_csv(logs, str(file_path))

    assert file_path.exists()
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)

    assert rows[0][0] == "id"
    assert rows[1][1] == "100"


# ---------------------------------------------------------------------
# TEST: PDF export creates file and content
# ---------------------------------------------------------------------

def test_export_logs_pdf_creates_file(tmp_path):
    logs = _create_dummy_logs(1)
    file_path = tmp_path / "logs.pdf"
    export_logs_pdf(logs, str(file_path))

    assert file_path.exists()
    assert file_path.stat().st_size > 0
