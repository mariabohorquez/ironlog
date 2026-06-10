from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
import models, schemas

router = APIRouter(prefix="/exercises", tags=["exercises"])


@router.get("/", response_model=list[schemas.ExerciseOut])
def list_exercises(
    category: str | None = Query(None),
    muscle: str | None = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(models.Exercise)
    if category:
        q = q.filter(models.Exercise.category == category)
    if muscle:
        q = q.filter(
            models.Exercise.primary_muscles.contains(muscle)
            | models.Exercise.secondary_muscles.contains(muscle)
        )
    return q.all()


@router.get("/{exercise_id}", response_model=schemas.ExerciseOut)
def get_exercise(exercise_id: int, db: Session = Depends(get_db)):
    ex = db.query(models.Exercise).filter(models.Exercise.id == exercise_id).first()
    if not ex:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Exercise not found")
    return ex
