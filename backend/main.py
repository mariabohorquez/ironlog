from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from database import engine
import models
from routers import users, exercises, workouts, bodyweight, analytics, calories
from seed import seed

models.Base.metadata.create_all(bind=engine)
seed()

app = FastAPI(title="Workout Planner API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(exercises.router)
app.include_router(workouts.router)
app.include_router(bodyweight.router)
app.include_router(analytics.router)
app.include_router(calories.router)

frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")
