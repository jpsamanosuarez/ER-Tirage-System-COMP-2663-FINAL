# patient_gui.py
from nicegui import ui
import datetime
from database import insert_patient

# --------------------------------------
# Symptom severity weights (ER realistic)
# --------------------------------------
SYMPTOM_WEIGHTS = {
    "Chest Pain": 10,
    "Difficulty Breathing": 10,
    "Stroke Symptoms (FAST)": 10,
    "Severe Bleeding": 9,
    "Head Injury": 8,
    "High Fever": 6,
    "Fracture": 5,
    "Abdominal Pain": 4,
    "Dizziness": 3,
    "Vomiting": 3,
    "Minor Cut / Bruise": 1,
}

def calculate_symptom_score(selected):
    return sum(SYMPTOM_WEIGHTS[s] for s in selected)

def calculate_age_weight(age: int):
    return (age - 65) * 0.5 if age > 65 else 0

def calculate_pain_weight(pain):
    return pain * 1.5


# --------------------------------------
# Patient Intake Page
# --------------------------------------
def build_patient_intake_page():

    ui.markdown("## **MTJ Coders — ER Patient Intake**").classes(
        "text-center text-2xl font-bold mb-6"
    )

    with ui.card().classes("mx-auto w-[650px] p-6 shadow-lg space-y-4"):

        # --------------------------------------
        # PERSONAL INFORMATION
        # --------------------------------------
        ui.label("Personal Information").classes("text-xl font-bold")
        first_name = ui.input("First Name").classes("w-full")
        last_name = ui.input("Last Name").classes("w-full mt-2")
        phone = ui.input("Phone Number").classes("w-full mt-2")
        age = ui.number("Age", min=0, max=120).classes("w-full mt-2")

        ui.separator()

        # --------------------------------------
        # SYMPTOMS
        # --------------------------------------
        ui.label("Symptoms & Condition").classes("text-xl font-bold")
        ui.markdown("Select **all symptoms you are experiencing**.")

        symptom_checks = {
            symptom: ui.checkbox(symptom).classes("mt-1")
            for symptom in SYMPTOM_WEIGHTS.keys()
        }

        ui.separator()

        # --------------------------------------
        # DURATION + PAIN SCALE
        # --------------------------------------
        duration = ui.input("Duration of Current Symptoms (e.g., 2 hours)").classes("w-full")

        ui.markdown("### 🩸 Pain Level (0 = none, 10 = worst)").classes(
            "text-lg font-bold mt-4"
        )
        pain = ui.slider(min=0, max=10, value=0).classes("w-full")

        with ui.row().classes("gap-6 mt-2"):
            is_pregnant = ui.checkbox("Pregnant")
            mobility = ui.checkbox("Mobility Issues")

        ui.separator()

        # --------------------------------------
        # NOTES
        # --------------------------------------
        ui.label("Additional Notes").classes("text-xl font-bold")
        notes = ui.textarea("Optional notes").classes("w-full")

        ui.separator()

        # --------------------------------------
        # PRIORITY PREVIEW
        # --------------------------------------
        priority_label = ui.label("Priority Score: 0.0").classes(
            "text-lg font-bold text-blue-600"
        )

        def update_priority_preview():
            selected = [sym for sym, box in symptom_checks.items() if box.value]

            symptom_score = calculate_symptom_score(selected)
            age_w = calculate_age_weight(age.value or 0)
            pain_w = calculate_pain_weight(pain.value or 0)

            result = symptom_score + age_w + pain_w
            if is_pregnant.value:
                result += 5
            if mobility.value:
                result += 3
            if "Stroke Symptoms (FAST)" in selected:
                result += 50

            priority_label.text = f"Priority Score: {round(result, 2)}"

        # Bind updates
        age.on('update:modelValue', lambda e: update_priority_preview())
        pain.on('update:modelValue', lambda e: update_priority_preview())
        is_pregnant.on('update:modelValue', lambda e: update_priority_preview())
        mobility.on('update:modelValue', lambda e: update_priority_preview())
        for chk in symptom_checks.values():
            chk.on('update:modelValue', lambda e: update_priority_preview())

        ui.separator()

        # --------------------------------------
        # SUBMIT PATIENT
        # --------------------------------------
        def submit_patient():
            try:
                selected = [sym for sym, box in symptom_checks.items() if box.value]

                symptom_score = calculate_symptom_score(selected)
                age_w = calculate_age_weight(age.value)
                pain_w = calculate_pain_weight(pain.value)

                overall_priority = (
                    symptom_score
                    + age_w
                    + pain_w
                    + (5 if is_pregnant.value else 0)
                    + (3 if mobility.value else 0)
                    + (50 if "Stroke Symptoms (FAST)" in selected else 0)
                )

                insert_patient({
                    "first_name": first_name.value,
                    "last_name": last_name.value,
                    "phone": phone.value,
                    "age": age.value,
                    "symptoms": ",".join(selected),
                    "duration": duration.value,
                    "pain_level": pain.value,
                    "is_pregnant": int(is_pregnant.value),
                    "mobility_issues": int(mobility.value),
                    "stroke_alert": int("Stroke Symptoms (FAST)" in selected),
                    "temperature": None,
                    "bp_systolic": None,
                    "bp_diastolic": None,
                    "heart_rate": None,
                    "respiratory_rate": None,
                    "triage_notes": notes.value,
                    "symptom_score": symptom_score,
                    "age_weight": age_w,
                    "pain_weight": pain_w,
                    "overall_priority": overall_priority,
                    "status": "Waiting",
                    "arrival_time": datetime.datetime.now().isoformat()
                })

                ui.notify("Patient Registered Successfully!", color="green")

                # Reset fields
                first_name.set_value("")
                last_name.set_value("")
                phone.set_value("")
                duration.set_value("")
                age.set_value(0)
                pain.set_value(0)
                for box in symptom_checks.values():
                    box.set_value(False)
                is_pregnant.set_value(False)
                mobility.set_value(False)
                notes.set_value("")
                priority_label.text = "Priority Score: 0.0"

            except Exception as e:
                print("❌ ERROR:", e)
                ui.notify(f"Error: {e}", color="red")

        ui.button(
            "Submit Patient",
            on_click=submit_patient,
            color="blue"
        ).classes("w-full text-white font-bold mt-6")

        ui.markdown(
            "<div style='text-align:center; opacity:0.6; margin-top:20px;'>"
            "MTJ Coders © 2025</div>"
        )
