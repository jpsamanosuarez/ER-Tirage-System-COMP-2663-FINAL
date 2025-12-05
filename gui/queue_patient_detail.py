# gui/queue_patient_detail.py

from nicegui import ui
from core.queue_manager import QueueManager
from database import get_connection

qm = QueueManager()


def queue_patient_detail_page(patient_id: int):

    patient = qm.get_patient_by_id(patient_id)

    if not patient:
        ui.label("❌ Patient not found").classes("text-red-600 text-xl")
        return

    # ---------------------------------------------------
    # HEADER
    # ---------------------------------------------------
    ui.label(f"Patient Detail – {patient.full_name}") \
        .classes("text-3xl font-bold mb-4")

    ui.button(
        "⬅ Back to Queue Dashboard",
        on_click=lambda: ui.navigate.to("/queue"),
    ).classes("mb-6")

    # ---------------------------------------------------
    # MAIN CARD
    # ---------------------------------------------------
    with ui.card().classes("p-6 shadow-lg bg-white w-full md:w-3/4 space-y-6"):

        # ==========================
        # BASIC INFO
        # ==========================
        ui.label("👤 Basic Information").classes("text-xl font-semibold")

        ui.markdown(
            f"""
            **Name:** {patient.full_name}  
            **Age:** {patient.age}  
            **Phone:** {patient.phone}  
            **Status:** {patient.status}  
            **Arrival:** {patient.arrival_time}  
        """
        )

        # ==========================
        # SYMPTOMS
        # ==========================
        ui.label("🩺 Symptoms").classes("text-xl font-semibold")
        ui.markdown(", ".join(patient.symptoms) if patient.symptoms else "None")

        # ==========================
        # VITALS
        # ==========================
        ui.label("🧪 Vitals").classes("text-xl font-semibold")

        ui.markdown(
            f"""
            - **Heart Rate:** {patient.heart_rate or '--'}  
            - **Blood Pressure:** {patient.bp_systolic or '--'}/{patient.bp_diastolic or '--'}  
            - **Respiratory Rate:** {patient.respiratory_rate or '--'}  
            - **Temperature:** {patient.temperature or '--'}  
        """
        )

        # ==========================
        # PRIORITY
        # ==========================
        priority_value = qm.calculate_priority(patient)

        ui.label("📊 Priority Score").classes("text-xl font-semibold")
        ui.label(f"{priority_value}") \
            .classes("text-2xl font-bold text-blue-600")

        # ==========================
        # NURSE NOTES
        # ==========================
        ui.label("📝 Nurse Notes").classes("text-xl font-semibold")
        ui.markdown(patient.triage_notes or "No notes recorded.")

        # ==========================
        # UPDATE STATUS
        # ==========================
        ui.label("🔄 Update Patient Status").classes("text-xl font-semibold")

        status_select = ui.select(
            ["Waiting", "In Treatment", "Completed"],
            value=patient.status,
        ).classes("w-1/3")

        def save_status():
            conn = get_connection()
            conn.execute(
                "UPDATE patients SET status=? WHERE id=?",
                (status_select.value, patient_id),
            )
            conn.commit()
            conn.close()

            ui.notify("Status updated!", color="green")
            ui.navigate.to("/queue")

        ui.button("Save Status", color="green", on_click=save_status)
