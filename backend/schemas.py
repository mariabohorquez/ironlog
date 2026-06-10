from pydantic import BaseModel
from datetime import date
from typing import Optional


# ── User ────────────────────────────────────────────────
class UserCreate(BaseModel):
    name: str
    age: int
    sex: str
    height_cm: float
    activity_level: float = 1.55
    body_fat_pct: Optional[float] = None


class UserOut(UserCreate):
    id: int
    model_config = {"from_attributes": True}


# ── Exercise ────────────────────────────────────────────
class ExerciseOut(BaseModel):
    id: int
    name: str
    category: str
    primary_muscles: str
    secondary_muscles: str
    gif_url: Optional[str]
    description: Optional[str]
    model_config = {"from_attributes": True}


# ── WorkoutSet ──────────────────────────────────────────
class SetCreate(BaseModel):
    exercise_id: int
    set_number: int
    reps: int
    weight_kg: float
    rpe: Optional[float] = None


class SetOut(SetCreate):
    id: int
    workout_id: int
    exercise: ExerciseOut
    model_config = {"from_attributes": True}


# ── Workout ─────────────────────────────────────────────
class WorkoutCreate(BaseModel):
    user_id: int
    date: date
    name: str
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None


class WorkoutOut(WorkoutCreate):
    id: int
    sets: list[SetOut] = []
    model_config = {"from_attributes": True}


# ── BodyWeight ──────────────────────────────────────────
class BodyWeightCreate(BaseModel):
    user_id: int
    date: date
    weight_kg: float


class BodyWeightOut(BodyWeightCreate):
    id: int
    model_config = {"from_attributes": True}


# ── Calories ────────────────────────────────────────────
class CalcInput(BaseModel):
    weight_kg: float
    height_cm: float
    age: int
    sex: str
    activity_level: float
    body_fat_pct: Optional[float] = None


class CalcResult(BaseModel):
    mifflin_bmr: float
    harris_bmr: float
    katch_bmr: Optional[float]
    mifflin_tdee: float
    harris_tdee: float
    katch_tdee: Optional[float]


class ProjectionInput(BaseModel):
    current_weight_kg: float
    target_weight_kg: float
    weekly_change_kg: float  # positive = gain, negative = cut
    tdee: float


class ProjectionResult(BaseModel):
    daily_delta_kcal: float
    weeks_to_target: float
    target_date: date
    daily_intake_goal: float
