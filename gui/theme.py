from nicegui import ui


def apply_theme():
    """Apply global colors and basic CSS."""
    ui.colors(
        primary='#1565C0',
        secondary='#26A69A',
        accent='#FFB300',
        positive='#2E7D32',
        negative='#C62828',
        info='#0288D1',
        warning='#F9A825',
    )

    ui.add_head_html("""
    <style>
        body {
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background-color: #f5f7fb;
        }
    </style>
    """)
