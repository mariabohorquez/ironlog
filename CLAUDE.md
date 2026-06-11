# IronLog — Workout Planner

Fitness tracking app: workout logging, muscle heatmap, BMR/TDEE calculator, 1RM estimates, weight projection.

## Stack
- **Backend**: Python 3.11 · FastAPI · SQLAlchemy · SQLite (`backend/workout.db`)
- **Frontend**: Vanilla HTML/CSS/JS · Chart.js (CDN) · no build step
- **Server**: `uvicorn main:app --reload` from `backend/`

## Folder map
```
backend/
  main.py          ← FastAPI app, CORS, static mount, seed on startup
  database.py      ← SQLAlchemy engine + SessionLocal + Base
  models.py        ← User, Exercise, Workout, WorkoutSet, BodyWeightLog
  schemas.py       ← Pydantic schemas (Create/Out)
  seed.py          ← 65 exercises seeded on first run
  routers/
    users.py       ← CRUD /users
    exercises.py   ← GET /exercises (filter by category, muscle)
    workouts.py    ← CRUD /workouts + /workouts/{id}/sets
    bodyweight.py  ← POST/GET /bodyweight
    analytics.py   ← /analytics/volume, /analytics/1rm
    calories.py    ← /calories/calculate, /calories/projection
frontend/
  index.html       ← single-page app, all views inside
  css/style.css    ← dark theme (MacroFactor-inspired)
  js/
    api.js         ← fetch wrapper, all API calls
    heatmap.js     ← muscle heatmap renderer (MertenD image assets, non-commercial license)
    app.js         ← navigation, all page logic
```

## Conventions
- All Python functions must have type hints
- FastAPI routes: explicit `response_model` and `status_code`
- After touching any router, regenerate `openapi.yaml`:
  `python -c "import json,yaml,main; open('../openapi.yaml','w').write(yaml.dump(json.loads(main.app.openapi().__str__())))"`
- No external JS dependencies beyond Chart.js (already on CDN)
- Run tests before finishing any feature: `cd backend && python -m pytest` (if tests exist)

## Muscle slug mapping (SVG ↔ DB)
Front: chest, abs, obliques, biceps, triceps, deltoids, trapezius, forearm, quadriceps, adductors, calves, tibialis
Back: upper-back, lower-back, gluteal, hamstring, trapezius, deltoids, triceps, calves, adductors, forearm

## Key formulas
- BMR Mifflin: `(10·w) + (6.25·h) - (5·age) + (5 if M else -161)`
- BMR Harris: `13.397·w + 4.799·h - 5.677·age + 88.362` (M)
- BMR Katch-McArdle: `370 + 21.6 · lean_mass_kg`
- 1RM Epley: `weight × (1 + reps/30)`
- Weight projection: `Δweight_kg × 7700 / daily_deficit`
