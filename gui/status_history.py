# gui/status_history.py

from nicegui import ui
from database import get_connection
from datetime import datetime


# Translate DB status codes to human workflow statuses
def map_status_label(value):
    mapping = {
        "Waiting": "Waiting for Triage",
        "Waiting Treatment": "Waiting for Treatment",
        "In Treatment": "In Treatment",
        "Completed": "Completed",
        "Discharged": "Discharged",
    }
    return mapping.get(value, value or "Unknown")


def format_timedelta(delta):
    seconds = int(delta.total_seconds())
    if seconds < 60:
        return f"{seconds}s"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    if hours < 24:
        return f"{hours}h {minutes % 60}m"
    days = hours // 24
    return f"{days}d {hours % 24}h"


def status_history_page():
    ui.label("📝 Status History Logs").classes(
        "text-3xl font-bold text-blue-800 mb-6"
    )

    conn = get_connection()
    c = conn.cursor()

    # Fetch logs sorted by patient AND time
    c.execute("""
        SELECT 
            sh.patient_id,
            p.first_name || ' ' || p.last_name AS full_name,
            sh.old_status,
            sh.new_status,
            sh.timestamp,
            sh.notes
        FROM status_history sh
        JOIN patients p ON p.id = sh.patient_id
        ORDER BY sh.patient_id ASC, sh.timestamp ASC;
    """)

    logs = c.fetchall()

    # Build rows with delta calculations
    rows = []
    last_timestamp = {}

    for row in logs:
        pid = row["patient_id"]
        current_time = datetime.fromisoformat(row["timestamp"])

        if pid in last_timestamp:
            delta = format_timedelta(current_time - last_timestamp[pid])
        else:
            delta = "—"  # first entry for this patient

        last_timestamp[pid] = current_time

        rows.append({
            "patient": f"{pid} — {row['full_name']}",
            "old": map_status_label(row["old_status"]),
            "new": map_status_label(row["new_status"]),
            "time": row["timestamp"],
            "elapsed": delta,
            "notes": row["notes"] or "",
        })

    ui.table(
        columns=[
            {"name": "patient", "label": "Patient", "field": "patient"},
            {"name": "old", "label": "Old Status", "field": "old"},
            {"name": "new", "label": "New Status", "field": "new"},
            {"name": "time", "label": "Changed At", "field": "time"},
            {"name": "elapsed", "label": "Time Between Statuses", "field": "elapsed"},
            {"name": "notes", "label": "Notes", "field": "notes"},
        ],
        rows=rows,
    )
