# tests/test_patient_model.py

from core.patient import Patient
from datetime import datetime, timedelta

def test_validation_rules():
    # Invalid pain level
    try:
        Patient(
            id=1, first_name="A", last_name="B", phone="C",
            age=30, symptoms=[], duration="", pain_level=50
        )
        assert False
    except ValueError:
        assert True

    # Invalid age
    try:
        Patient(
            id=1, first_name="A", last_name="B", phone="C",
            age=150, symptoms=[], duration="", pain_level=2
        )
        assert False
    except ValueError:
        assert True


def test_symptom_parsing():
    p = Patient(
        id=1, first_name="A", last_name="B", phone="C",
        age=20, symptoms="Chest Pain,Head Injury",
        duration="", pain_level=5
    )
    assert p.symptoms == ["Chest Pain", "Head Injury"]


def test_wait_time_calculation():
    earlier = datetime.now() - timedelta(minutes=10)
    p = Patient(
        id=1, first_name="A", last_name="B", phone="C",
        age=40, symptoms=[], duration="", pain_level=3,
        arrival_time=earlier
    )
    assert 9 <= p.queue_time_minutes <= 11
