# tests/test_queue_manager.py

from core.patient import Patient
from core.queue_manager import QueueManager
from datetime import datetime, timedelta

qm = QueueManager()

def test_priority_simple():
    p = Patient(
        id=1, first_name="A", last_name="B", phone="C",
        age=25, symptoms=["Chest Pain"], duration="",
        pain_level=5, arrival_time=datetime.now()
    )
    score = qm.calculate_priority(p)
    assert score > 0


def test_stroke_priority():
    p = Patient(
        id=2, first_name="A", last_name="B", phone="C",
        age=50, symptoms=[], duration="",
        pain_level=1, is_code_stroke=True,
        arrival_time=datetime.now()
    )
    assert qm.calculate_priority(p) >= 50


def test_age_weight_effect():
    young = Patient(
        id=3, first_name="Y", last_name="Z", phone="C",
        age=20, symptoms=[], duration="",
        pain_level=1, arrival_time=datetime.now()
    )
    old = Patient(
        id=4, first_name="U", last_name="V", phone="C",
        age=90, symptoms=[], duration="",
        pain_level=1, arrival_time=datetime.now()
    )
    assert qm.calculate_priority(old) > qm.calculate_priority(young)
