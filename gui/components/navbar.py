# gui/components/navbar.py
from nicegui import ui

def navbar(active: str = None):
    """Top navigation bar used in all interfaces."""
    with ui.header().classes('bg-blue-600 text-white shadow-md'):
        with ui.row().classes('w-full justify-between items-center p-3'):
            # --- Left side (logo + title) ---
            with ui.row().classes('items-center gap-3'):
                ui.label('🏥 ER Triage & Queue Manager').classes('text-lg font-semibold')

            # --- Center navigation buttons ---
            with ui.row().classes('gap-4'):
                pages = {
                    'home': ('🏠 Home', '/home'),
                    'patient': ('🧍 Patient', '/patient'),
                    'nurse': ('💉 Nurse', '/nurse'),
                    'admin': ('🧠 Admin', '/admin'),
                }

                for key, (label, link) in pages.items():
                    color = 'white' if key != active else 'yellow-300'
                    ui.button(label, on_click=lambda l=link: ui.open(l)).props(
                        f'flat color={color}'
                    )

            # --- Right side watermark ---
            ui.label('MTJ Coders').classes('italic text-sm text-yellow-300')
