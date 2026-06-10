"""One-off demo data seeder — posts body weight logs and workouts through the
running API so all input is validated by the schemas. Dates are computed
relative to today so the dashboard's 7-day window always has data.

Usage: python seed_demo.py   (server must be running on port 8001)
"""
from datetime import date, timedelta

import httpx

BASE = "http://127.0.0.1:8001"
USER_ID = 1

TODAY = date.today()


def days_ago(n: int) -> str:
    return (TODAY - timedelta(days=n)).isoformat()


# (days ago, weight kg) — gentle downward trend into the current weight
WEIGHTS: list[tuple[int, float]] = [
    (42, 84.6), (38, 84.4), (35, 84.5), (31, 84.1), (28, 84.2),
    (24, 83.9), (21, 84.0), (17, 83.7), (14, 83.8), (10, 83.6),
    (7, 83.5), (4, 83.3), (1, 83.4),
]

# (days ago, name, [(exercise, sets, reps, kg), ...])
WORKOUTS: list[tuple[int, str, list[tuple[str, int, int, float]]]] = [
    (5, "Push Day", [
        ("Bench Press", 4, 8, 70), ("Incline Bench Press", 3, 10, 55),
        ("Overhead Press", 3, 8, 42.5), ("Lateral Raise", 3, 14, 10),
        ("Tricep Pushdown", 3, 12, 25),
    ]),
    (3, "Pull Day", [
        ("Deadlift", 4, 5, 120), ("Pull-up", 3, 8, 0),
        ("Barbell Row", 3, 10, 60), ("Bicep Curl", 3, 12, 14),
        ("Face Pull", 3, 15, 20),
    ]),
    (1, "Leg Day", [
        ("Barbell Back Squat", 4, 6, 95), ("Romanian Deadlift", 3, 10, 80),
        ("Leg Press", 3, 12, 160), ("Leg Curl", 3, 12, 45),
        ("Calf Raise", 4, 15, 60),
    ]),
]


def main() -> None:
    client = httpx.Client(base_url=BASE, timeout=10)

    exercises = client.get("/exercises/").json()
    by_name = {e["name"].lower(): e["id"] for e in exercises}

    # Skip dates that already have a workout (makes re-runs safe)
    existing = client.get(f"/workouts/?user_id={USER_ID}").json()
    existing_keys = {(w["date"], w["name"]) for w in existing}

    for ago, kg in WEIGHTS:
        client.post("/bodyweight/", json={
            "user_id": USER_ID, "date": days_ago(ago), "weight_kg": kg,
        }).raise_for_status()
    print(f"Logged {len(WEIGHTS)} body weight entries")

    for ago, name, items in WORKOUTS:
        d = days_ago(ago)
        if (d, name) in existing_keys:
            print(f"Skipping '{name}' ({d}) — already exists")
            continue
        w = client.post("/workouts/", json={
            "user_id": USER_ID, "date": d, "name": name,
        })
        w.raise_for_status()
        wid = w.json()["id"]
        n_sets = 0
        for ex_name, sets, reps, kg in items:
            ex_id = by_name.get(ex_name.lower())
            if ex_id is None:
                print(f"  ! exercise not found: {ex_name}")
                continue
            for set_number in range(1, sets + 1):
                client.post(f"/workouts/{wid}/sets", json={
                    "exercise_id": ex_id, "set_number": set_number,
                    "reps": reps, "weight_kg": kg, "rpe": None,
                }).raise_for_status()
                n_sets += 1
        print(f"Created '{name}' ({d}) with {n_sets} sets")


if __name__ == "__main__":
    main()
