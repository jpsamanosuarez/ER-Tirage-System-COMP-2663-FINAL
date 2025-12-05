from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Patient:
    id: int | None
    first_name: str
    last_name: str
    phone: str
    age: int

    # Symptom system
    symptoms: List[str] = field(default_factory=list)
    duration: str = ""
    pain_level: int = 0

    # Triage flags
    is_pregnant: bool = False
    mobility_issues: bool = False
    is_code_stroke: bool = False

    # Vitals
    temperature: Optional[float] = None
    bp_systolic: Optional[int] = None
    bp_diastolic: Optional[int] = None
    heart_rate: Optional[int] = None
    respiratory_rate: Optional[int] = None

    # Nurse input
    triage_notes: str = ""

    # Priority components
    symptom_score: float = 0.0
    age_weight: float = 0.0
    pain_weight: float = 0.0
    overall_priority: float = 0.0

    # Admin fields
    status: str = "Waiting"
    arrival_time: datetime | None = None
    room: Optional[str] = None  # ⭐ NEW ⭐

    # ----------------------------------------------------
    def __post_init__(self):

        # Normalize fields
        self.pain_level = self.pain_level or 0
        self.symptom_score = self.symptom_score or 0
        self.age_weight = self.age_weight or 0
        self.pain_weight = self.pain_weight or 0
        self.overall_priority = self.overall_priority or 0
        self.age = self.age or 0

        # Convert symptoms from string → list
        if isinstance(self.symptoms, str):
            self.symptoms = (
                [s.strip() for s in self.symptoms.split(",")] if self.symptoms else []
            )

        # Normalize status
        valid_statuses = {
            "waiting": "Waiting",
            "in treatment": "In Treatment",
            "treatment": "In Treatment",
            "completed": "Completed",
            "discharged": "Completed",
        }
        self.status = valid_statuses.get(self.status.lower(), "Waiting")

        # Validate input ranges
        if not (0 <= self.age <= 120):
            raise ValueError("Age must be between 0–120.")
        if not (0 <= self.pain_level <= 10):
            raise ValueError("Pain level must be between 0–10.")

        # Convert arrival_time properly
        if isinstance(self.arrival_time, str):
            if self.arrival_time in ("", "None"):
                self.arrival_time = datetime.now()
            else:
                self.arrival_time = datetime.fromisoformat(self.arrival_time)

        if self.arrival_time is None:
            self.arrival_time = datetime.now()

    # ----------------------------------------------------
    @property
    def queue_time_minutes(self) -> float:
        delta = datetime.now() - self.arrival_time
        return round(delta.total_seconds() / 60, 1)

    # ----------------------------------------------------
    def to_db_tuple(self):
        """Convert into correct DB column order INCLUDING room."""
        return (
            self.first_name,
            self.last_name,
            self.phone,
            self.age,
            ",".join(self.symptoms),
            self.duration,
            self.pain_level,
            int(self.is_pregnant),
            int(self.mobility_issues),
            int(self.is_code_stroke),
            self.temperature,
            self.bp_systolic,
            self.bp_diastolic,
            self.heart_rate,
            self.respiratory_rate,
            self.triage_notes,
            self.symptom_score,
            self.age_weight,
            self.pain_weight,
            self.overall_priority,
            self.status,
            self.arrival_time.isoformat(),
            self.room,  # ⭐ NEW ⭐
        )

    # ----------------------------------------------------
    @staticmethod
    def from_db_row(row):
        return Patient(
            id=row["id"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            phone=row["phone"],
            age=row["age"],
            symptoms=row["symptoms"],
            duration=row["duration"],
            pain_level=row["pain_level"],
            is_pregnant=bool(row["is_pregnant"]),
            mobility_issues=bool(row["mobility_issues"]),
            is_code_stroke=bool(row["stroke_alert"]),
            temperature=row["temperature"],
            bp_systolic=row["bp_systolic"],
            bp_diastolic=row["bp_diastolic"],
            heart_rate=row["heart_rate"],
            respiratory_rate=row["respiratory_rate"],
            triage_notes=row["triage_notes"],
            symptom_score=row["symptom_score"],
            age_weight=row["age_weight"],
            pain_weight=row["pain_weight"],
            overall_priority=row["overall_priority"],
            status=row["status"],
            arrival_time=row["arrival_time"],
            room=row["room"],  # ⭐ NEW ⭐
        )

    # ----------------------------------------------------
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def priority_score(self):
        return self.overall_priority

    def __str__(self):
        return (
            f"{self.full_name} | Age: {self.age} | Pain: {self.pain_level} | "
            f"Priority: {self.overall_priority} | Waiting: {self.queue_time_minutes} min"
        )
