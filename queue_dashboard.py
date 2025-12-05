# gui/queue_dashboard.py

from nicegui import ui
from core.queue_manager import QueueManager
from database import get_connection
from core.status_logger import log_status_change

qm = QueueManager()

# -----------------------------------------------------------
# STATUS CHIP
# -----------------------------------------------------------
def status_chip(status: str):
    colors = {
        "Waiting": "#3B82F6",             # Blue
        "Waiting Treatment": "#6366F1",   # Indigo
        "In Treatment": "#F59E0B",        # Orange
        "Completed": "#10B981",           # Green
        "Discharged": "#6B7280",          # Gray
    }
    color = colors.get(status, "#6B7280")

    with ui.row().classes("items-center gap-1"):
        ui.icon("circle").style(f"color:{color}; font-size:13px")
        ui.label(status).classes("text-sm font-semibold")


# -----------------------------------------------------------
# PRIORITY CHIP
# -----------------------------------------------------------
def priority_chip(score: float):
    if score >= 300:
        label, color = "Critical", "#DC2626"
    elif score >= 150:
        label, color = "Urgent", "#F59E0B"
    else:
        label, color = "Stable", "#16A34A"

    with ui.row().classes("items-center gap-1"):
        ui.icon("priority_high").style(f"color:{color}; font-size:18px")
        ui.label(f"{label} ({int(score)})").style(f"color:{color}; font-weight:600;")


# -----------------------------------------------------------
# ASSIGN ROOM POPUP (with status logging)
# -----------------------------------------------------------
def open_assign_room_dialog(patient, refresh_fn):

    dialog = ui.dialog()

    with dialog, ui.card().classes("p-6 w-[400px] shadow-xl space-y-4"):
        ui.label(f"Assign Room • {patient.full_name}").classes("text-xl font-bold")
        room_field = ui.input("Room (ER-5, Trauma-4, Bed-12)").classes("w-full")

        def save_room():
            room = (room_field.value or "").strip()
            if not room:
                ui.notify("Room cannot be empty!", color="red")
                return

            conn = get_connection()
            old_status = conn.execute(
                "SELECT status FROM patients WHERE id=?", (patient.id,)
            ).fetchone()["status"]

            conn.execute(
                "UPDATE patients SET room=?, status='In Treatment' WHERE id=?",
                (room, patient.id),
            )
            conn.commit()
            conn.close()

            # LOG
            log_status_change(patient.id, old_status, "In Treatment", f"Assigned room {room}")

            dialog.close()
            ui.notify(f"Assigned room {room}", color="green")
            refresh_fn()

        ui.button("Save", on_click=save_room, color="blue").classes("w-full text-white font-bold")
        ui.button("Cancel", on_click=dialog.close, color="gray").classes("w-full")

    dialog.open()


# -----------------------------------------------------------
# DISCHARGE (with status logging)
# -----------------------------------------------------------
def discharge_patient(pid, refresh_fn):
    conn = get_connection()

    old_status = conn.execute("SELECT status FROM patients WHERE id=?", (pid,)).fetchone()["status"]

    conn.execute("UPDATE patients SET status='Completed' WHERE id=?", (pid,))
    conn.commit()
    conn.close()

    log_status_change(pid, old_status, "Completed", "Discharged from ER")

    ui.notify("Patient marked as Completed", color="green")
    refresh_fn()


# -----------------------------------------------------------
# DELETE
# -----------------------------------------------------------
def delete_patient(patient_id: int, refresh_fn):
    conn = get_connection()
    conn.execute("DELETE FROM patients WHERE id=?", (patient_id,))
    conn.commit()
    conn.close()
    ui.notify("Patient deleted", color="red")
    refresh_fn()


# -----------------------------------------------------------
# PATIENT CARD (FINAL FIXED VERSION)
# -----------------------------------------------------------
def create_patient_card(p, refresh_fn):

    score = qm.calculate_priority(p)
    norm_status = (p.status or "").strip().lower().replace("_", " ")

    card = ui.card().classes(
        "w-full p-0 mb-4 shadow hover:shadow-xl transition-all rounded-xl border overflow-hidden"
    )

    with card:

        # ----------- TOP CLICKABLE SECTION (NOT covering buttons) -----------
        top = ui.row().classes(
            "p-5 cursor-pointer hover:bg-gray-50 bg-white border-b"
        )
        top.on("click", lambda _: ui.navigate.to(f"/queue/{p.id}"))

        with top:
            with ui.column().classes("w-full"):

                with ui.row().classes("justify-between items-center"):
                    ui.label(p.full_name).classes("text-xl font-bold")
                    status_chip(p.status)

                priority_chip(score)

                with ui.row().classes("text-sm text-gray-700 mt-2 gap-6"):
                    ui.label(f"Age: {p.age}")
                    ui.label(f"Arrived: {p.arrival_time}")

                if p.room:
                    ui.label(f"Room: {p.room}") \
                        .classes("mt-1 text-blue-700 font-semibold")

                ui.label("Symptoms:").classes("mt-3 font-semibold text-sm")
                ui.label(", ".join(p.symptoms) if p.symptoms else "None") \
                    .classes("text-sm text-gray-700")

                with ui.row().classes("mt-3 text-sm gap-6"):
                    ui.label(f"Temp: {p.temperature or '--'}°C")
                    ui.label(f"HR: {p.heart_rate or '--'} bpm")
                    ui.label(f"BP: {(p.bp_systolic or '--')}/{(p.bp_diastolic or '--')}")
                    ui.label(f"RR: {p.respiratory_rate or '--'}/min")

        # ----------- BUTTON SECTION -----------
        with ui.row().classes("gap-3 p-4 bg-gray-100 flex-wrap justify-end"):

            # FIX: Assign Room after triage, tolerant of capitalization/spacing
            if norm_status == "waiting treatment":
                ui.button("Assign Room", icon="meeting_room", color="blue") \
                    .classes("text-white font-bold").on(
                        "click",
                        lambda _: open_assign_room_dialog(p, refresh_fn),
                        ["prevent", "stop"]
                    )

            ui.button("Re-Triage", icon="edit", color="orange") \
                .classes("text-white font-bold").on(
                    "click",
                    lambda _: ui.navigate.to(f"/nurse/{p.id}"),
                    ["prevent", "stop"]
                )

            if norm_status != "completed":
                ui.button("Discharge", icon="logout", color="green") \
                    .classes("text-white font-bold").on(
                        "click",
                        lambda _: discharge_patient(p.id, refresh_fn),
                        ["prevent", "stop"]
                    )

            ui.button("Delete", icon="delete", color="red") \
                .classes("text-white font-bold").on(
                    "click",
                    lambda _: delete_patient(p.id, refresh_fn),
                    ["prevent", "stop"]
                )


# -----------------------------------------------------------
# MAIN QUEUE DASHBOARD PAGE
# -----------------------------------------------------------
@ui.page("/queue")
def queue_dashboard_page():

    ui.label("🏥 Emergency Department — Queue Dashboard") \
        .classes("text-3xl font-bold mb-5")

    FILTER = {"value": "Waiting"}

    # ---- Status Filter Buttons ----
    with ui.row().classes("gap-3 mb-4"):
        for label in ["Waiting", "Waiting Treatment", "In Treatment", "Completed", "All"]:
            ui.button(
                label,
                on_click=lambda l=label: (
                    FILTER.update({"value": l}),
                    ui.notify(f"Filter → {l}", color="blue"),
                    refresh.refresh()
                )
            ).props("outline").classes("text-sm")

    cards_container = ui.column().classes("w-full")

    @ui.refreshable
    def refresh():
        cards_container.clear()

        all_patients = qm.fetch_all_patients()
        f = FILTER["value"]

        if f != "All":
            visible = [p for p in all_patients if p.status == f]
        else:
            visible = all_patients

        visible = sorted(visible, key=lambda p: qm.calculate_priority(p), reverse=True)

        for p in visible:
            create_patient_card(p, refresh.refresh)

    refresh()
    ui.timer(6, refresh.refresh)

    return cards_container
