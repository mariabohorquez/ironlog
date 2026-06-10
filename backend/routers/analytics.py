from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta
from collections import defaultdict
from database import get_db
import models

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/volume")
def muscle_volume(
    user_id: int = Query(...),
    days: int = Query(7),
    db: Session = Depends(get_db),
):
    """Returns total sets per muscle slug for the last N days."""
    since = date.today() - timedelta(days=days)
    workouts = (
        db.query(models.Workout)
        .filter(models.Workout.user_id == user_id, models.Workout.date >= since)
        .all()
    )
    volume: dict[str, int] = defaultdict(int)
    for w in workouts:
        for s in w.sets:
            for slug in s.exercise.primary_muscles.split(","):
                slug = slug.strip()
                if slug:
                    volume[slug] += 1
            for slug in s.exercise.secondary_muscles.split(","):
                slug = slug.strip()
                if slug:
                    volume[slug] += 0  # secondary contributes 0 to set count
    return {"volume": dict(volume), "days": days}


@router.get("/1rm")
def one_rm_estimates(
    user_id: int = Query(...),
    exercise_id: int = Query(...),
    db: Session = Depends(get_db),
):
    """Returns estimated 1RM per workout date using 4 formulas."""
    workouts = (
        db.query(models.Workout)
        .filter(models.Workout.user_id == user_id)
        .order_by(models.Workout.date.asc())
        .all()
    )
    results = []
    for w in workouts:
        sets_for_ex = [s for s in w.sets if s.exercise_id == exercise_id]
        if not sets_for_ex:
            continue
        best = max(sets_for_ex, key=lambda s: s.weight_kg * (1 + s.reps / 30))
        r, wt = best.reps, best.weight_kg
        epley = wt * (1 + r / 30)
        brzycki = wt * (36 / (37 - r)) if r < 37 else wt * 1.33
        lombardi = wt * (r ** 0.10)
        oconner = wt * (1 + r / 40)
        avg = (epley + brzycki + lombardi + oconner) / 4
        results.append({
            "date": str(w.date),
            "epley": round(epley, 1),
            "brzycki": round(brzycki, 1),
            "lombardi": round(lombardi, 1),
            "oconner": round(oconner, 1),
            "average": round(avg, 1),
        })
    return {"exercise_id": exercise_id, "history": results}
