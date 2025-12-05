# gui/admin_gui.py

from nicegui import ui

def admin_panel_page():

    ui.markdown(
        """
        <div style="text-align:center; margin-top:10px;">
            <h1 style="font-size:36px; font-weight:bold; color:#1e3a8a;">
                ⚙️ Admin Control Center
            </h1>
            <p style="font-size:18px; opacity:0.75;">
                System oversight, queue monitoring, and configuration tools
            </p>
        </div>
        """
    )

    ui.separator().classes("my-6")

    # --- ADMIN DASHBOARD CARDS ---
    with ui.row().classes("w-full justify-center gap-8 mt-4 flex-wrap"):

        # Queue Management Card
        with ui.card().classes(
            "p-6 w-[260px] shadow-lg hover:shadow-2xl transition-all duration-200"
        ):
            ui.label("📊 Queue Dashboard").classes("text-xl font-bold mb-2 text-blue-700")
            ui.markdown("View the current triage queue and patient priorities.")
            ui.button(
                "Open Dashboard",
                color="blue",
                on_click=lambda: ui.navigate.to('/queue')
            ).classes("w-full mt-3 text-white font-bold")

        # User Tools Card — Coming Soon
        with ui.card().classes(
            "p-6 w-[260px] shadow-lg hover:shadow-2xl transition-all duration-200"
        ):
            ui.label("👤 User Management").classes("text-xl font-bold mb-2 text-blue-700")
            ui.markdown("Add, remove, or configure system roles and accounts.")
            ui.button(
                "Coming Soon",
                color="gray",
                on_click=lambda: ui.notify("👤 User Management is under development.")
            ).classes("w-full mt-3 text-white font-bold")

        # System Logs Card — NOW WORKING
        with ui.card().classes(
            "p-6 w-[260px] shadow-lg hover:shadow-2xl transition-all duration-200"
        ):
            ui.label("📝 Status History").classes("text-xl font-bold mb-2 text-blue-700")
            ui.markdown("Review patient status changes and triage audit logs.")
            ui.button(
                "View Logs",
                color="blue",
                on_click=lambda: ui.navigate.to('/status_history')
            ).classes("w-full mt-3 text-white font-bold")

    ui.separator().classes("my-8")

    # --- SYSTEM STATUS ---
    ui.label("System Status: 🟢 Online") \
        .classes("text-green-600 text-xl font-bold text-center")

    ui.separator().classes("my-8")

    # --- FOOTER ---
    ui.markdown(
        """
        <div style='text-align:center; margin-top:15px; opacity:0.6; font-size:14px;'>
            MTJ Coders © 2025<br>
            ER Triage & Queue Manager — Admin Panel
        </div>
        """
    )
