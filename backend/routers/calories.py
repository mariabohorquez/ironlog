from fastapi import APIRouter
from datetime import date, timedelta
import math
from schemas import CalcInput, CalcResult, ProjectionInput, ProjectionResult

router = APIRouter(prefix="/calories", tags=["calories"])

KCAL_PER_KG_FAT = 7700.0


def _mifflin(w: float, h: float, age: int, sex: str) -> float:
    base = 10 * w + 6.25 * h - 5 * age
    return base + 5 if sex.upper() == "M" else base - 161


def _harris(w: float, h: float, age: int, sex: str) -> float:
    if sex.upper() == "M":
        return 13.397 * w + 4.799 * h - 5.677 * age + 88.362
    return 9.247 * w + 3.098 * h - 4.330 * age + 447.593


def _katch(w: float, body_fat_pct: float) -> float:
    lean_mass = w * (1 - body_fat_pct / 100)
    return 370 + 21.6 * lean_mass


@router.post("/calculate", response_model=CalcResult)
def calculate_calories(data: CalcInput):
    mifflin = _mifflin(data.weight_kg, data.height_cm, data.age, data.sex)
    harris = _harris(data.weight_kg, data.height_cm, data.age, data.sex)
    katch = _katch(data.weight_kg, data.body_fat_pct) if data.body_fat_pct else None

    return CalcResult(
        mifflin_bmr=round(mifflin, 1),
        harris_bmr=round(harris, 1),
        katch_bmr=round(katch, 1) if katch else None,
        mifflin_tdee=round(mifflin * data.activity_level, 1),
        harris_tdee=round(harris * data.activity_level, 1),
        katch_tdee=round(katch * data.activity_level, 1) if katch else None,
    )


@router.post("/projection", response_model=ProjectionResult)
def weight_projection(data: ProjectionInput):
    daily_delta = data.weekly_change_kg * KCAL_PER_KG_FAT / 7
    delta_weight = data.target_weight_kg - data.current_weight_kg
    weeks = abs(delta_weight / data.weekly_change_kg) if data.weekly_change_kg != 0 else 0
    target_date = date.today() + timedelta(days=math.ceil(weeks * 7))
    daily_intake = data.tdee + daily_delta

    return ProjectionResult(
        daily_delta_kcal=round(daily_delta, 1),
        weeks_to_target=round(weeks, 1),
        target_date=target_date,
        daily_intake_goal=round(daily_intake, 1),
    )
