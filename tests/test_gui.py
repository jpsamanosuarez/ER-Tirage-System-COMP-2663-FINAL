# tests/test_gui.py

from gui.components.patient_gui import build_patient_intake_page
from gui.components.nurse_gui import nurse_triage_page
from gui.queue_dashboard import queue_dashboard_page

def test_patient_gui_loads():
    try:
        build_patient_intake_page()
    except Exception:
        assert False

def test_nurse_gui_loads():
    try:
        nurse_triage_page()
    except Exception:
        assert False

def test_queue_dashboard_loads():
    try:
        queue_dashboard_page()
    except Exception:
        assert False
