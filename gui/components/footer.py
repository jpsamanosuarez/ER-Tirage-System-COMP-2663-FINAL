# gui/components/footer.py
from nicegui import ui
from datetime import datetime

def footer():
    """Bottom footer displayed on every page."""
    year = datetime.now().year
    with ui.footer().classes('bg-gray-100 text-gray-700 text-center p-3 shadow-inner'):
        ui.markdown(
            f'© {year} **MTJ Coders** | ER Triage & Queue Manager  |  Acadia University'
        ).classes('text-sm')
