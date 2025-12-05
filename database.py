import sqlite3
import os

# Path to SQLite database inside /data folder
DB_PATH = os.path.join("data", "er_triage.db")


# -----------------------------------------------------------
# CONNECTION (ensures dict-like row access)
# -----------------------------------------------------------
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # CRITICAL
    return conn


# -----------------------------------------------------------
# INITIALIZE + MIGRATE DATABASE
# -----------------------------------------------------------
def init_database():
    """Initialize database and ensure all required columns exist."""
    os.makedirs("data", exist_ok=True)
    conn = get_connection()

    # Base table creation
    conn.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name TEXT,
        phone TEXT,
        age INTEGER,
        symptoms TEXT,
        duration TEXT,
        pain_level INTEGER,

        is_pregnant INTEGER DEFAULT 0,
        mobility_issues INTEGER DEFAULT 0,
        stroke_alert INTEGER DEFAULT 0,

        temperature REAL,
        bp_systolic INTEGER,
        bp_diastolic INTEGER,
        heart_rate INTEGER,
        respiratory_rate INTEGER,

        triage_notes TEXT DEFAULT "",

        symptom_score REAL DEFAULT 0,
        age_weight REAL DEFAULT 0,
        pain_weight REAL DEFAULT 0,
        overall_priority REAL DEFAULT 0,

        status TEXT DEFAULT 'Waiting',
        arrival_time TEXT,

        room TEXT DEFAULT NULL
    );
    """)

    # Required columns (for migration)
    REQUIRED_COLUMNS = [
        ("duration", "TEXT"),
        ("is_pregnant", "INTEGER DEFAULT 0"),
        ("mobility_issues", "INTEGER DEFAULT 0"),
        ("temperature", "REAL"),
        ("bp_systolic", "INTEGER"),
        ("bp_diastolic", "INTEGER"),
        ("heart_rate", "INTEGER"),
        ("respiratory_rate", "INTEGER"),
        ("triage_notes", "TEXT DEFAULT ''"),
        ("symptom_score", "REAL DEFAULT 0"),
        ("age_weight", "REAL DEFAULT 0"),
        ("pain_weight", "REAL DEFAULT 0"),
        ("overall_priority", "REAL DEFAULT 0"),
        ("arrival_time", "TEXT"),
        ("room", "TEXT"),
    ]

    existing_cols = {
        row["name"]
        for row in conn.execute("PRAGMA table_info(patients);").fetchall()
    }

    # Add missing columns
    for col, definition in REQUIRED_COLUMNS:
        if col not in existing_cols:
            print(f"[DB MIGRATION] Adding missing column: {col}")
            conn.execute(f"ALTER TABLE patients ADD COLUMN {col} {definition};")

    # Status history table (official schema using timestamp ONLY)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS status_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        old_status TEXT,
        new_status TEXT,
        timestamp TEXT NOT NULL,
        notes TEXT DEFAULT '',
        FOREIGN KEY(patient_id) REFERENCES patients(id)
    );
    """)

    conn.commit()
    conn.close()


# -----------------------------------------------------------
# INSERT PATIENT (Used by Intake Form)
# -----------------------------------------------------------
def insert_patient(data: dict):
    conn = get_connection()

    conn.execute("""
        INSERT INTO patients (
            first_name, last_name, phone, age,
            symptoms, duration, pain_level,
            is_pregnant, mobility_issues, stroke_alert,
            temperature, bp_systolic, bp_diastolic,
            heart_rate, respiratory_rate,
            triage_notes,
            symptom_score, age_weight, pain_weight, overall_priority,
            status, arrival_time, room
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (
        data["first_name"],
        data["last_name"],
        data["phone"],
        data["age"],
        data["symptoms"],
        data["duration"],
        data["pain_level"],
        data["is_pregnant"],
        data["mobility_issues"],
        data["stroke_alert"],
        data.get("temperature"),
        data.get("bp_systolic"),
        data.get("bp_diastolic"),
        data.get("heart_rate"),
        data.get("respiratory_rate"),
        data.get("triage_notes", ""),
        data["symptom_score"],
        data["age_weight"],
        data["pain_weight"],
        data["overall_priority"],
        data.get("status", "Waiting"),
        data["arrival_time"],
        data.get("room")
    ))

    conn.commit()
    conn.close()


# -----------------------------------------------------------
# UTILITY FUNCTIONS
# -----------------------------------------------------------
def get_all_patients():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM patients ORDER BY id DESC;").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_patient_status(patient_id: int, new_status: str, notes: str = ""):
    conn = get_connection()

    old_status = conn.execute(
        "SELECT status FROM patients WHERE id = ?;",
        (patient_id,)
    ).fetchone()

    old_status = old_status["status"] if old_status else "Unknown"

    conn.execute(
        "UPDATE patients SET status=? WHERE id=?;",
        (new_status, patient_id),
    )

    conn.execute("""
        INSERT INTO status_history (patient_id, old_status, new_status, notes, timestamp)
        VALUES (?, ?, ?, ?, datetime('now'));
    """, (patient_id, old_status, new_status, notes))

    conn.commit()
    conn.close()


def update_stroke_alert(patient_id: int, stroke_flag: int):
    conn = get_connection()
    conn.execute(
        "UPDATE patients SET stroke_alert=? WHERE id=?;",
        (stroke_flag, patient_id),
    )
    conn.commit()
    conn.close()
