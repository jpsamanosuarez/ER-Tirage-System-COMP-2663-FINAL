# core/status_logger.py

from database import get_connection
from datetime import datetime

def log_status_change(patient_id: int, old_status: str, new_status: str, notes: str = ""):
  
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        INSERT INTO status_history (patient_id, old_status, new_status, notes, timestamp)
        VALUES (?, ?, ?, ?, ?);
    """, (
        patient_id,
        old_status,
        new_status,
        notes,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()
