"""
Basic smoke tests for the IronLog API.
Run from backend/ with: python -m pytest tests/ -v
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# ── Exercises ──────────────────────────────────────────────────────────────
class TestExercises:
    def test_list_returns_seeded_data(self):
        r = client.get("/exercises/")
        assert r.status_code == 200
        data = r.json()
        assert len(data) >= 60

    def test_list_contains_bench_press(self):
        r = client.get("/exercises/")
        names = [e["name"] for e in r.json()]
        assert "Bench Press" in names

    def test_exercise_schema_fields(self):
        r = client.get("/exercises/")
        ex = r.json()[0]
        for field in ("id", "name", "category", "primary_muscles", "secondary_muscles"):
            assert field in ex, f"Missing field: {field}"

    def test_filter_by_category(self):
        r = client.get("/exercises/?category=push")
        assert r.status_code == 200
        data = r.json()
        assert all(e["category"] == "push" for e in data)

    def test_gif_url_populated_for_bench_press(self):
        r = client.get("/exercises/")
        bench = next(e for e in r.json() if e["name"] == "Bench Press")
        assert bench["gif_url"] is not None
        assert "cdn.jsdelivr.net" in bench["gif_url"]


# ── Users ──────────────────────────────────────────────────────────────────
class TestUsers:
    def test_create_user(self):
        r = client.post("/users/", json={
            "name": "Test User",
            "age": 30,
            "sex": "M",
            "height_cm": 175.0,
            "activity_level": 1.55,
        })
        assert r.status_code == 201
        data = r.json()
        assert data["name"] == "Test User"
        assert "id" in data

    def test_list_users(self):
        r = client.get("/users/")
        assert r.status_code == 200
        assert isinstance(r.json(), list)


# ── Workouts ───────────────────────────────────────────────────────────────
class TestWorkouts:
    def _create_user(self) -> int:
        r = client.post("/users/", json={
            "name": "Workout Tester",
            "age": 25,
            "sex": "M",
            "height_cm": 180.0,
            "activity_level": 1.375,
        })
        return r.json()["id"]

    def test_create_workout(self):
        uid = self._create_user()
        r = client.post("/workouts/", json={
            "user_id": uid,
            "date": "2026-05-30",
            "name": "Push Day",
        })
        assert r.status_code == 201
        data = r.json()
        assert data["name"] == "Push Day"
        assert data["user_id"] == uid
        assert data["sets"] == []

    def test_list_workouts_for_user(self):
        uid = self._create_user()
        client.post("/workouts/", json={"user_id": uid, "date": "2026-05-30", "name": "W1"})
        r = client.get(f"/workouts/?user_id={uid}")
        assert r.status_code == 200
        assert len(r.json()) >= 1

    def test_add_set_to_workout(self):
        uid = self._create_user()
        r = client.post("/workouts/", json={"user_id": uid, "date": "2026-05-30", "name": "Leg Day"})
        wid = r.json()["id"]
        exercises = client.get("/exercises/").json()
        eid = exercises[0]["id"]

        r = client.post(f"/workouts/{wid}/sets", json={
            "exercise_id": eid,
            "set_number": 1,
            "reps": 10,
            "weight_kg": 60.0,
        })
        assert r.status_code == 201
        data = r.json()
        assert data["reps"] == 10
        assert data["weight_kg"] == 60.0

    def test_delete_workout(self):
        uid = self._create_user()
        r = client.post("/workouts/", json={"user_id": uid, "date": "2026-05-30", "name": "Temp"})
        wid = r.json()["id"]
        r = client.delete(f"/workouts/{wid}")
        assert r.status_code == 204

    def test_get_nonexistent_workout_returns_404(self):
        r = client.get("/workouts/999999")
        assert r.status_code == 404


# ── Calories ───────────────────────────────────────────────────────────────
class TestCalories:
    def test_calculate_bmr_mifflin(self):
        r = client.post("/calories/calculate", json={
            "weight_kg": 80.0,
            "height_cm": 180.0,
            "age": 30,
            "sex": "M",
            "activity_level": 1.55,
        })
        assert r.status_code == 200
        data = r.json()
        assert "mifflin_bmr" in data
        assert "mifflin_tdee" in data
        # Mifflin-St Jeor for 80kg/180cm/30yo male ≈ 1878 kcal
        assert 1600 < data["mifflin_bmr"] < 2200
        assert data["mifflin_tdee"] > data["mifflin_bmr"]

    def test_calculate_bmr_female(self):
        r = client.post("/calories/calculate", json={
            "weight_kg": 60.0,
            "height_cm": 165.0,
            "age": 28,
            "sex": "F",
            "activity_level": 1.375,
        })
        assert r.status_code == 200
        data = r.json()
        assert data["mifflin_bmr"] > 0
        # Female BMR should be lower than same-stats male
        r_m = client.post("/calories/calculate", json={
            "weight_kg": 60.0, "height_cm": 165.0, "age": 28,
            "sex": "M", "activity_level": 1.375,
        })
        assert data["mifflin_bmr"] < r_m.json()["mifflin_bmr"]

    def test_katch_mccardle_requires_body_fat(self):
        r = client.post("/calories/calculate", json={
            "weight_kg": 75.0, "height_cm": 178.0, "age": 25,
            "sex": "M", "activity_level": 1.55,
            "body_fat_pct": 15.0,
        })
        assert r.status_code == 200
        assert r.json()["katch_bmr"] is not None


# ── Analytics ──────────────────────────────────────────────────────────────
class TestAnalytics:
    def test_volume_returns_dict(self):
        r = client.post("/users/", json={
            "name": "Volume User", "age": 28, "sex": "M",
            "height_cm": 175.0, "activity_level": 1.55,
        })
        uid = r.json()["id"]
        r = client.get(f"/analytics/volume?user_id={uid}&days=7")
        assert r.status_code == 200
        data = r.json()
        assert "volume" in data
        assert "days" in data
        assert data["days"] == 7

    def test_volume_counts_sets_correctly(self):
        r = client.post("/users/", json={
            "name": "Counter User", "age": 30, "sex": "F",
            "height_cm": 165.0, "activity_level": 1.375,
        })
        uid = r.json()["id"]
        r = client.post("/workouts/", json={
            "user_id": uid, "date": "2026-05-30", "name": "Chest Day",
        })
        wid = r.json()["id"]
        bench = next(e for e in client.get("/exercises/").json() if e["name"] == "Bench Press")

        for i in range(1, 4):
            client.post(f"/workouts/{wid}/sets", json={
                "exercise_id": bench["id"],
                "set_number": i,
                "reps": 8,
                "weight_kg": 70.0,
            })

        r = client.get(f"/analytics/volume?user_id={uid}&days=7")
        volume = r.json()["volume"]
        assert volume.get("chest", 0) == 3
