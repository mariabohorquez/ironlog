from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from database import get_db
import models, schemas

router = APIRouter(prefix="/bodyweight", tags=["bodyweight"])


@router.post("/", response_model=schemas.BodyWeightOut, status_code=201)
def log_weight(entry: schemas.BodyWeightCreate, db: Session = Depends(get_db)):
    db_entry = models.BodyWeightLog(**entry.model_dump())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


@router.get("/", response_model=list[schemas.BodyWeightOut])
def get_weight_log(
    user_id: int = Query(...),
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(models.BodyWeightLog).filter(models.BodyWeightLog.user_id == user_id)
    if from_date:
        q = q.filter(models.BodyWeightLog.date >= from_date)
    if to_date:
        q = q.filter(models.BodyWeightLog.date <= to_date)
    return q.order_by(models.BodyWeightLog.date.asc()).all()
