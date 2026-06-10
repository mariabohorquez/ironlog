from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from database import get_db
import models, schemas

router = APIRouter(prefix="/workouts", tags=["workouts"])


@router.post("/", response_model=schemas.WorkoutOut, status_code=201)
def create_workout(workout: schemas.WorkoutCreate, db: Session = Depends(get_db)):
    db_workout = models.Workout(**workout.model_dump())
    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)
    return db_workout


@router.get("/", response_model=list[schemas.WorkoutOut])
def list_workouts(
    user_id: int = Query(...),
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(models.Workout).filter(models.Workout.user_id == user_id)
    if from_date:
        q = q.filter(models.Workout.date >= from_date)
    if to_date:
        q = q.filter(models.Workout.date <= to_date)
    return q.order_by(models.Workout.date.desc()).all()


@router.get("/{workout_id}", response_model=schemas.WorkoutOut)
def get_workout(workout_id: int, db: Session = Depends(get_db)):
    workout = db.query(models.Workout).filter(models.Workout.id == workout_id).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    return workout


@router.delete("/{workout_id}", status_code=204)
def delete_workout(workout_id: int, db: Session = Depends(get_db)):
    workout = db.query(models.Workout).filter(models.Workout.id == workout_id).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    db.delete(workout)
    db.commit()


@router.post("/{workout_id}/sets", response_model=schemas.SetOut, status_code=201)
def add_set(workout_id: int, s: schemas.SetCreate, db: Session = Depends(get_db)):
    workout = db.query(models.Workout).filter(models.Workout.id == workout_id).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    db_set = models.WorkoutSet(workout_id=workout_id, **s.model_dump())
    db.add(db_set)
    db.commit()
    db.refresh(db_set)
    return db_set


@router.delete("/sets/{set_id}", status_code=204)
def delete_set(set_id: int, db: Session = Depends(get_db)):
    s = db.query(models.WorkoutSet).filter(models.WorkoutSet.id == set_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Set not found")
    db.delete(s)
    db.commit()
