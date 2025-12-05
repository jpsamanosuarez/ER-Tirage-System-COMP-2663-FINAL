from nicegui import ui

# GUI imports
from gui.patient_gui import build_patient_intake_page
from gui.admin_gui import admin_panel_page
from gui.nurse_gui import nurse_patient_list_page, nurse_triage_page
from gui.queue_patient_detail import queue_patient_detail_page
from gui.status_history import status_history_page

# Dashboard (root)
from queue_dashboard import queue_dashboard_page

# Initialization
from database import init_database

print("🚀 Starting ER Triage & Queue Manager...")
init_database()
print("[INIT] Database ready.")

# -------------------------------------------------------
# MAIN LAYOUT WRAPPER
# -------------------------------------------------------
def layout(page_builder):
    with ui.row().classes("w-full h-full") as root:

        # Sidebar
        with ui.column().classes(
            "bg-gray-900 text-white w-[220px] min-w-[220px] h-screen p-6 space-y-6 shadow-lg"
        ):
            ui.markdown("""
            ## 🏥 ER Triage
            ### MTJ Coders
            """).classes("font-bold text-white")

            ui.link("➕ Patient Intake", "/patient").classes("text-lg hover:text-blue-400")
            ui.link("🩺 Nurse Triage", "/nurse").classes("text-lg hover:text-blue-400")
            ui.link("📋 Queue Dashboard", "/queue").classes("text-lg hover:text-blue-400")
            ui.link("⚙️ Admin Tools", "/admin").classes("text-lg hover:text-blue-400")

        # Main Content
        with ui.column().classes("flex-1 p-10 overflow-auto"):
            page_builder()

            ui.markdown(
                "<div style='text-align:center; opacity:0.5; margin-top:50px;'>"
                "MTJ Coders © 2025 — ER Triage & Queue Manager"
                "</div>"
            )

    return root


# -------------------------------------------------------
# ROUTES
# -------------------------------------------------------

@ui.page("/")
def home_page():

    def home_content():

        ui.markdown("""
        <div style="text-align:center; margin-top:20px;">
            <h1 style="font-size:42px; font-weight:800; color:#1e3a8a; margin-bottom:10px;">
                Welcome to the ER Triage & Queue Manager
            </h1>
            <p style="font-size:18px; color:#4b5563; max-width:650px; margin:0 auto;">
                A complete hospital triage system that streamlines patient intake, 
                nurse assessments, real-time queue monitoring, and administrative tools.
            </p>
        </div>
        """)

        ui.separator().classes("my-10 w-2/3 mx-auto")

        with ui.row().classes("justify-center gap-10 mt-4"):

            # Patient Intake
            with ui.card().classes("p-6 w-[260px] shadow-lg hover:shadow-2xl transition-all duration-200"):
                ui.label("➕ Patient Intake").classes("text-xl font-semibold text-blue-700 mb-1")
                ui.markdown("**Register a new patient entering the ER**").classes("text-gray-600 mb-3")
                ui.button("Open", color="blue",
                          on_click=lambda: ui.navigate.to('/patient')).classes("w-full text-white")

            # Nurse Triage
            with ui.card().classes("p-6 w-[260px] shadow-lg hover:shadow-2xl transition-all duration-200"):
                ui.label("🩺 Nurse Triage").classes("text-xl font-semibold text-blue-700 mb-1")
                ui.markdown("**View assigned patients and record vitals**").classes("text-gray-600 mb-3")
                ui.button("Open", color="blue",
                          on_click=lambda: ui.navigate.to('/nurse')).classes("w-full text-white")

            # Queue Dashboard
            with ui.card().classes("p-6 w-[260px] shadow-lg hover:shadow-2xl transition-all duration-200"):
                ui.label("📋 Queue Dashboard").classes("text-xl font-semibold text-blue-700 mb-1")
                ui.markdown("**Monitor patient queue and triage priority**").classes("text-gray-600 mb-3")
                ui.button("Open", color="blue",
                          on_click=lambda: ui.navigate.to('/queue')).classes("w-full text-white")

            # Admin Tools
            with ui.card().classes("p-6 w-[260px] shadow-lg hover:shadow-2xl transition-all duration-200"):
                ui.label("⚙️ Admin Tools").classes("text-xl font-semibold text-blue-700 mb-1")
                ui.markdown("**Configuration & system management**").classes("text-gray-600 mb-3")
                ui.button("Open", color="blue",
                          on_click=lambda: ui.navigate.to('/admin')).classes("w-full text-white")

    return layout(home_content)


@ui.page("/patient")
def patient_page():
    return layout(build_patient_intake_page)


@ui.page("/nurse")
def nurse_page():
    return layout(nurse_patient_list_page)


# Dynamic nurse triage route
@ui.page("/nurse/{patient_id}")
def nurse_patient_page(patient_id: int):
    return layout(lambda: nurse_triage_page(int(patient_id)))


@ui.page("/queue")
def queue_page():
    return layout(queue_dashboard_page)


@ui.page("/queue/{patient_id}")
def queue_detail_page(patient_id: int):
    return layout(lambda: queue_patient_detail_page(int(patient_id)))


@ui.page("/admin")
def admin_page():
    return layout(admin_panel_page)


# -------------------------------------------------------
# STATUS HISTORY ROUTE (NEW)
# -------------------------------------------------------
@ui.page("/status_history")
def status_history_route():
    return layout(status_history_page)


# -------------------------------------------------------
# START NICEGUI
# -------------------------------------------------------
ui.run(port=8080, reload=False)
