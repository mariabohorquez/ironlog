# IronLog 🏋️

A full-stack fitness tracking app: log workouts, visualize weekly muscle volume on an interactive body heatmap, track body weight, estimate 1RM progression, and plan calorie targets.

Built with **FastAPI + SQLAlchemy + SQLite** on the backend and **vanilla HTML/CSS/JS** (no build step) on the frontend — developed end-to-end with [Claude Code](https://claude.com/claude-code).

## Features

- **Dashboard** — weekly set count vs last week, body weight with trend sparkline, workout streak, muscle volume heatmap, recent workouts
- **Muscle heatmap** — interactive SVG body diagram; muscles are colored by weekly training volume, with pixel-perfect hover tooltips (image assets from [MertenD/musclegroup-image-generator](https://github.com/MertenD/musclegroup-image-generator), MIT)
- **Workout logger** — start an empty session or quick-start from Push / Pull / Legs templates; per-set reps, weight, and RPE
- **Exercise library** — 65 seeded exercises with illustrations, searchable and filterable by category (Push / Pull / Legs / Core)
- **Analytics** — body weight chart, volume by muscle, estimated 1RM history (Epley & Brzycki)
- **Stats & goals** — BMR/TDEE calculator (Mifflin, Harris-Benedict, Katch-McArdle) and weight goal projection

## Quick start

```bash
# 1. Create a virtualenv and install dependencies
python -m venv venv
venv\Scripts\activate          # Windows  (source venv/bin/activate on Unix)
pip install -r requirements.txt

# 2. Run the server (seeds the database on first run)
cd backend
uvicorn main:app --reload

# 3. Open the app
# http://localhost:8000  — frontend
# http://localhost:8000/docs — interactive API docs (Swagger)
```

## Project structure

```
backend/
  main.py          FastAPI app, CORS, static mount, seed on startup
  database.py      SQLAlchemy engine + session
  models.py        User, Exercise, Workout, WorkoutSet, BodyWeightLog
  schemas.py       Pydantic request/response schemas
  seed.py          65 exercises seeded on first run
  routers/         users, exercises, workouts, bodyweight, analytics, calories
frontend/
  index.html       single-page app (all views)
  css/style.css    dark theme
  js/api.js        fetch wrapper for all API calls
  js/heatmap.js    SVG muscle heatmap renderer
  js/app.js        navigation + page logic
.claude/
  rules/           project rules (API design, frontend, Python style, security)
  commands/        custom skills — /gen-workout generates workout templates
  settings.json    tool permissions for Claude Code
openapi.yaml       generated OpenAPI spec
```

## Claude Code integration

This project is configured for agent-assisted development:

- **`CLAUDE.md`** — project context: stack, folder map, conventions, domain formulas
- **`.claude/rules/`** — enforced conventions (explicit `response_model` on every route, type hints everywhere, all colors via CSS variables, no raw `fetch()` outside `api.js`, …)
- **`.claude/settings.json`** — permission allow/deny lists (e.g. blocks `rm -rf`, `git push --force`)
- **`/gen-workout <target>`** — custom slash command that builds a workout plan from the exercise database

## Key formulas

| Metric | Formula |
|---|---|
| BMR (Mifflin-St Jeor) | `10·kg + 6.25·cm − 5·age + (5 ♂ / −161 ♀)` |
| BMR (Katch-McArdle) | `370 + 21.6 · lean mass kg` |
| Estimated 1RM (Epley) | `weight × (1 + reps/30)` |
| Goal projection | `Δkg × 7700 kcal / daily deficit` |
