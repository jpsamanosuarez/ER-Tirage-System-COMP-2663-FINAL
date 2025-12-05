# core/queue_manager.py

from datetime import datetime
from typing import List, Optional
from core.patient import Patient
from database import get_connection
from core.status_logger import log_status_change


class QueueManager:
    def __init__(self):
        self.conn = get_connection()

    # -------------------------------------------------------
    # RETURN ALL PATIENTS
    # -------------------------------------------------------
    def fetch_all_patients(self) -> List[Patient]:
        c = self.conn.cursor()
        c.execute("SELECT * FROM patients ORDER BY arrival_time ASC;")
        rows = c.fetchall()
        return [Patient.from_db_row(r) for r in rows]

    # -------------------------------------------------------
    # RETURN ONLY WAITING PATIENTS
    # -------------------------------------------------------
    def fetch_waiting_patients(self) -> List[Patient]:
        c = self.conn.cursor()
        c.execute("SELECT * FROM patients WHERE status='Waiting';")
        rows = c.fetchall()
        return [Patient.from_db_row(r) for r in rows]

    # -------------------------------------------------------
    # TRIAGE PRIORITY ALGORITHM
    # -------------------------------------------------------
    def calculate_priority(self, p: Patient) -> float:

        score = 0.0

        # --- SYMPTOMS ---
        if p.symptoms:
            score += len(p.symptoms) * 2  # +2 per symptom

        # --- TEMPERATURE ---
        if p.temperature is not None:
            if p.temperature < 35:
                score += 6
            elif p.temperature > 39:
                score += 4

        # --- HEART RATE ---
        if p.heart_rate is not None:
            if p.heart_rate < 50 or p.heart_rate > 120:
                score += 6

        # --- RESPIRATORY RATE ---
        if p.respiratory_rate is not None:
            if p.respiratory_rate < 10 or p.respiratory_rate > 24:
                score += 8

        # --- BLOOD PRESSURE ---
        if p.bp_systolic is not None:
            if p.bp_systolic < 90:
                score += 10
            elif p.bp_systolic > 180:
                score += 6

        # --- PAIN LEVEL ---
        if p.pain_level is not None:
            score += p.pain_level * 1.5

        # --- AGE WEIGHT ---
        if p.age > 65:
            score += (p.age - 65) * 0.5

        # --- STROKE FLAG ---
        if p.is_code_stroke:
            score += 50

        # --- WAITING TIME ---
        if p.arrival_time:
            try:
                arrival = datetime.fromisoformat(p.arrival_time)
                wait_minutes = (datetime.now() - arrival).total_seconds() / 60
                score += wait_minutes * 0.25
            except:
                pass

        return round(score, 2)

    # -------------------------------------------------------
    # ORDER WAITING PATIENTS BY PRIORITY
    # -------------------------------------------------------
    def get_ordered_queue(self) -> List[Patient]:
        patients = self.fetch_waiting_patients()
        return sorted(patients, key=self.calculate_priority, reverse=True)

    # -------------------------------------------------------
    # DASHBOARD PATIENTS
    # -------------------------------------------------------
    def get_all_patients_for_dashboard(self) -> List[Patient]:
        return self.fetch_all_patients()

    # -------------------------------------------------------
    # GET PATIENT BY ID
    # -------------------------------------------------------
    def get_patient_by_id(self, patient_id: int) -> Optional[Patient]:
        c = self.conn.cursor()
        c.execute("SELECT * FROM patients WHERE id=?;", (patient_id,))
        row = c.fetchone()
        return Patient.from_db_row(row) if row else None

    # -------------------------------------------------------
    # UPDATE STATUS + LOG HISTORY
    # -------------------------------------------------------
    def update_status(self, patient_id: int, new_status: str, notes: str = ""):
        """Updates patient status AND logs the change in status_history."""
        c = self.conn.cursor()

        # Get the old status
        c.execute("SELECT status FROM patients WHERE id=?;", (patient_id,))
        row = c.fetchone()
        old_status = row["status"] if row else "Unknown"

        # Update DB
        c.execute("UPDATE patients SET status=? WHERE id=?;", (new_status, patient_id))
        self.conn.commit()

        # Log in history
        log_status_change(patient_id, old_status, new_status, notes)
