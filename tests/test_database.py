# tests/test_database.py

import os
import sqlite3
from data.database import init_database, insert_patient, get_all_patients, update_stroke_alert, update_patient_status, DB_PATH

def test_database_initialization():
    # Remove old DB to test re-initialization
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    init_database()
    assert os.path.exists(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cols = {c[1] for c in conn.execute("PRAGMA table_info(patients);")}
    conn.close()

    REQUIRED = {
        "first_name", "last_name", "phone", "age", "symptoms", "duration",
        "pain_level", "is_pregnant", "mobility_issues", "stroke_alert",
        "temperature", "bp_systolic", "bp_diastolic", "heart_rate",
        "respiratory_rate", "triage_notes", "symptom_score",
        "age_weight", "pain_weight", "overall_priority", "status",
        "arrival_time"
    }

    assert REQUIRED.issubset(cols)


def test_insert_and_fetch():
    init_database()

    insert_patient({
        "first_name": "John",
        "last_name": "Doe",
        "phone": "12345",
        "age": 40,
        "symptoms": "Chest Pain",
        "duration": "1 hour",
        "pain_level": 7,
        "is_pregnant": 0,
        "mobility_issues": 0,
        "stroke_alert": 0,
        "temperature": None,
        "bp_systolic": None,
        "bp_diastolic": None,
        "heart_rate": None,
        "respiratory_rate": None,
        "triage_notes": "",
        "symptom_score": 10,
        "age_weight": 0,
        "pain_weight": 10.5,
        "overall_priority": 20.5,
        "status": "Waiting",
        "arrival_time": "2025-01-01T12:00:00",
    })

    patients = get_all_patients()
    assert len(patients) > 0
    p = patients[0]

    assert p["first_name"] == "John"
    assert p["pain_level"] == 7


def test_updates():
    init_database()

    # Insert sample patient
    insert_patient({
        "first_name": "Jane",
        "last_name": "Smith",
        "phone": "999",
        "age": 60,
        "symptoms": "Head Injury",
        "duration": "2h",
        "pain_level": 5,
        "is_pregnant": 0,
        "mobility_issues": 1,
        "stroke_alert": 0,
        "temperature": None,
        "bp_systolic": None,
        "bp_diastolic": None,
        "heart_rate": None,
        "respiratory_rate": None,
        "triage_notes": "",
        "symptom_score": 8,
        "age_weight": 0,
        "pain_weight": 7.5,
        "overall_priority": 15.5,
        "status": "Waiting",
        "arrival_time": "2025-01-01T12:00:00",
    })

    pid = get_all_patients()[0]["id"]

    update_stroke_alert(pid, 1)
    update_patient_status(pid, "In Treatment", "initial triage done")

    updated = get_all_patients()[0]

    assert updated["stroke_alert"] == 1
    assert updated["status"] == "In Treatment"
    assert updated["notes"] == "initial triage done"
