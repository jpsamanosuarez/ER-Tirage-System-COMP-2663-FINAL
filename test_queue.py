# test_queue.py
from data.database import init_db, get_connection
from core.queue_manager import QueueManager
from datetime import datetime, timedelta

init_db()
conn = get_connection()
c = conn.cursor()

# Clear existing data
c.execute("DELETE FROM patients;")

# Add test data
patients = [
    ("John Doe", "555-1000", 45, "Chest pain", 8, "", "", 0, "Waiting", 9.0, datetime.now().isoformat()),
    ("Elder Anna", "555-2000", 78, "Weakness", 5, "", "", 0, "Waiting", 6.0, datetime.now().isoformat()),
    ("Stroke Bob", "555-3000", 62, "Slurred speech", 7, "", "", 1, "Waiting", 7.5, (datetime.now() - timedelta(minutes=10)).isoformat()),
]

c.executemany("""
INSERT INTO patients (name, contact, age, symptoms, pain_level, vitals, triage_notes,
                      is_code_stroke, status, severity_score, arrival_time)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
""", patients)
conn.commit()
conn.close()

# Run the queue
qm = QueueManager()
qm.print_queue()
