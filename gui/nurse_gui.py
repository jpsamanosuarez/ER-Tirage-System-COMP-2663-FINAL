# gui/nurse_gui.py

from nicegui import ui
from database import (
    get_all_patients,
    update_patient_status,
    update_stroke_alert,
    DB_PATH,
)
from core.queue_manager import QueueManager
import sqlite3
import datetime

qm = QueueManager()

# ==========================================================
# UTILITY HELPERS
# ==========================================================

def clean_symptoms(sym_str):
    if not sym_str:
        return []
    return [s.strip() for s in sym_str.split(",") if s.strip()]


def triage_badge(p):
    """Badge that displays triage state."""
    if p["stroke_alert"]:
        ui.label("🚨 Stroke Alert").classes("bg-red-600 text-white px-3 py-1 rounded-lg text-sm font-bold")
        return

    triaged = (
        p["temperature"] is not None
        or p["heart_rate"] is not None
        or p["bp_systolic"] is not None
    )

    if triaged:
        ui.label("🟢 Triaged").classes("bg-green-600 text-white px-3 py-1 rounded-lg text-sm font-bold")
    else:
        ui.label("🟡 Needs Triage").classes("bg-yellow-500 text-white px-3 py-1 rounded-lg text-sm font-bold")


def waiting_time(arrival_str):
    try:
        t0 = datetime.datetime.fromisoformat(arrival_str)
        mins = (datetime.datetime.now() - t0).total_seconds() // 60
        if mins < 60:
            return f"{int(mins)} min"
        return f"{int(mins//60)}h {int(mins%60)}m"
    except:
        return "Unknown"


# ==========================================================
# PATIENT LIST PAGE (Improved UX)
# ==========================================================
def nurse_patient_list_page():

    ui.markdown("## 🏥 Nurse Triage Panel — Patient List").classes("text-3xl font-bold mb-6")

    patients = get_all_patients()

    if not patients:
        ui.label("No patients available.").classes("text-gray-500")
        return

    for p in patients:
        symptoms = clean_symptoms(p["symptoms"])
        wait = waiting_time(p["arrival_time"])
        pr = p["overall_priority"] or 0

        card = ui.row().classes(
            f"p-5 bg-white shadow hover:shadow-xl cursor-pointer border-l-8 rounded-xl w-full mb-4"
        )

        with card:
            with ui.column().classes("w-full gap-1"):

                # Name + badge
                with ui.row().classes("items-center justify-between"):
                    ui.label(f"{p['first_name']} {p['last_name']}").classes("text-2xl font-bold")
                    triage_badge(p)

                # Symptoms
                ui.label(
                    "Symptoms: " + (", ".join(symptoms) if symptoms else "None")
                ).classes("text-gray-700 text-sm")

                # Vitals
                with ui.row().classes("gap-8 text-sm mt-1 text-gray-700"):
                    ui.label(f"Temp: {p['temperature'] or '--'}°C")
                    ui.label(f"HR: {p['heart_rate'] or '--'} bpm")
                    ui.label(f"BP: {(p['bp_systolic'] or '--')}/{p['bp_diastolic'] or '--'}")
                    ui.label(f"RR: {p['respiratory_rate'] or '--'}")

                # Footer details
                with ui.row().classes("gap-10 text-sm text-gray-800 mt-1"):
                    ui.label(f"Waiting: {wait}")
                    ui.label(f"Priority: {pr}")
                    ui.label(f"Status: {p['status']}")

        card.on("click", lambda e, pid=p["id"]: ui.navigate.to(f"/nurse/{pid}"))


# ==========================================================
# TRIAGE PAGE ROUTER
# ==========================================================
def nurse_triage_page(patient_id):

    patients = get_all_patients()
    p = next((x for x in patients if x["id"] == patient_id), None)

    if not p:
        ui.label("Patient not found").classes("text-red-600 text-xl")
        return

    ui.button("← Back", on_click=lambda: ui.navigate.to("/nurse")).classes("mb-4 bg-gray-700 text-white")

    ui.markdown(f"## 🧍 {p['first_name']} {p['last_name']} — Triage").classes("text-3xl font-bold mb-2")
    ui.label(f"Age: {p['age']} | Phone: {p['phone']} | Arrived: {p['arrival_time']}").classes("text-lg mb-4")

    # TRIAGED → show summary with RETRIAGE button
    already_triaged = (
        p["temperature"] is not None
        or p["heart_rate"] is not None
        or p["bp_systolic"] is not None
        or p["triage_notes"]
    )

    if already_triaged:
        return show_readonly_summary_with_retriage(p)

    return show_editable_triage_form(p)


# ==========================================================
# READ-ONLY SUMMARY (NOW WITH RETRIAGE BUTTON)
# ==========================================================
def show_readonly_summary_with_retriage(p):

    ui.markdown("### 📋 Completed Triage Summary").classes("text-2xl font-bold mb-4")

    with ui.card().classes("p-6 bg-gray-50 border space-y-2 shadow w-3/4"):

        ui.label(f"Temperature: {p['temperature']}°C")
        ui.label(f"BP: {p['bp_systolic']}/{p['bp_diastolic']}")
        ui.label(f"Heart Rate: {p['heart_rate']} bpm")
        ui.label(f"Resp Rate: {p['respiratory_rate']} /min")
        ui.label(f"Priority Score: {p['overall_priority']}")
        ui.label(f"Status: {p['status']}")

        ui.markdown("#### 📝 Notes").classes("font-bold")
        ui.label(p["triage_notes"] or "None")

    # ======= NEW FEATURE: RETRIAGE BUTTON =======
    def reset_triage():
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
        UPDATE patients
        SET temperature=NULL, bp_systolic=NULL, bp_diastolic=NULL,
            heart_rate=NULL, respiratory_rate=NULL, triage_notes=''
        WHERE id=?;
        """, (p["id"],))
        conn.commit()
        conn.close()

        ui.notify("Patient triage reset — ready for re-triage", color="blue")
        ui.navigate.to(f"/nurse/{p['id']}")

    ui.button("🔄 Re-Triage Patient", on_click=reset_triage)\
        .classes("mt-6 bg-blue-600 text-white px-4 py-2 rounded-lg font-bold")

    ui.button("← Back", on_click=lambda: ui.navigate.to("/nurse"))\
        .classes("mt-3 bg-gray-700 text-white px-4 py-2 rounded-lg")


# ==========================================================
# EDITABLE TRIAGE FORM (UPDATED & BP FIXED)
# ==========================================================
def show_editable_triage_form(p):

    ui.markdown("### ✏️ Nurse Triage Form").classes("text-2xl font-bold mt-4")

    with ui.row().classes("gap-10 w-full"):

        # LEFT — Vitals
        with ui.card().classes("p-5 w-1/2 shadow space-y-3"):
            ui.markdown("#### 🩺 Vitals").classes("font-bold")

            temp = ui.number("Temperature (°C)")
            bp_s = ui.number("BP Systolic (mmHg)")
            bp_d = ui.number("BP Diastolic (mmHg)")
            hr = ui.number("Heart Rate (bpm)")
            rr = ui.number("Respiratory Rate (/min)")
            pain = ui.number("Pain Level (0–10)", min=0, max=10)

            stroke = ui.switch("FAST Stroke Symptoms Present", value=bool(p["stroke_alert"]))

        # RIGHT — Notes
        with ui.card().classes("p-5 w-1/2 shadow space-y-3"):
            ui.markdown("#### 📝 Notes").classes("font-bold")
            notes = ui.textarea("Clinical Notes")

    # Priority preview
    preview = ui.label("Updated Priority: ---").classes(
        "text-xl font-bold text-blue-600 mt-4"
    )

    def recalc():
        from core.patient import Patient

        # Build patient object WITHOUT status (we assign status later)
        obj = Patient(
            id=p["id"],
            first_name=p["first_name"],
            last_name=p["last_name"],
            phone=p["phone"],
            age=p["age"],
            symptoms=clean_symptoms(p["symptoms"]),
            duration="",
            pain_level=pain.value or 0,
            is_pregnant=False,
            mobility_issues=False,
            is_code_stroke=stroke.value,
            temperature=temp.value,
            bp_systolic=bp_s.value,
            bp_diastolic=bp_d.value,
            heart_rate=hr.value,
            respiratory_rate=rr.value,
            triage_notes=notes.value,
            overall_priority=0,
            status="Waiting Treatment",    # always assigned on save
            arrival_time=datetime.datetime.fromisoformat(p["arrival_time"])
        )

        score = qm.calculate_priority(obj)
        preview.text = f"Updated Priority: {score}"
        return score

    # On-change recalc
    for f in [temp, bp_s, bp_d, hr, rr, pain, notes, stroke]:
        f.on("change", lambda e: recalc())

    # SAVE BUTTON (FIXED)
    def save():
        score = recalc()
        new_status = "Waiting Treatment"  # ALWAYS after triage

        # Update DB + history
        update_patient_status(p["id"], new_status, notes.value)
        update_stroke_alert(p["id"], int(stroke.value))

        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            UPDATE patients
            SET temperature=?, bp_systolic=?, bp_diastolic=?, heart_rate=?,
                respiratory_rate=?, triage_notes=?, overall_priority=?,
                status='Waiting Treatment'
            WHERE id=?;
        """, (
            temp.value, bp_s.value, bp_d.value, hr.value, rr.value,
            notes.value, score, p["id"]
        ))
        conn.commit()
        conn.close()

        ui.notify("Triage saved — patient moved to treatment queue", color="green")
        ui.navigate.to("/nurse")

    ui.button("💾 Save Triage", on_click=save)\
        .classes("mt-6 w-full bg-green-600 text-white font-bold rounded-lg")



