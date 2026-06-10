"""Run once to populate the exercise database; always keeps gif_urls fresh."""
from database import SessionLocal, engine
import models

models.Base.metadata.create_all(bind=engine)


def _gif(url: str | None) -> str | None:
    """Return the image URL as-is (already full URLs from simplyfitness.com CDN)."""
    return url or None


# (name, category, primary_muscles, secondary_muscles, description, gif_url)
# Images sourced from simplyfitness.com — Shopify CDN, no hotlink restrictions.
_SF = "https://cdn.shopify.com/s/files/1/0269/5551/3900/files"

EXERCISES = [
    # ── PUSH ──────────────────────────────────────────────────────────────
    ("Bench Press", "push", "chest", "deltoids,triceps",
     "Lie on bench, lower bar to chest, press up.",
     f"{_SF}/Barbell-Bench-Press_0316b783-43b2-44f8-8a2b-b177a2cfcbfc_600x600.png?v=1612137800"),
    ("Incline Bench Press", "push", "chest", "deltoids,triceps",
     "Bench set to 30-45°, targets upper chest.",
     f"{_SF}/Incline-Barbell-Bench-Press_dc0c6279-d038-44f5-a682-54c2a5e2602c_600x600.png?v=1612137944"),
    ("Decline Bench Press", "push", "chest", "triceps",
     "Bench set to -15°, targets lower chest.",
     f"{_SF}/Barbell-Declined-Bench-Press_600x600.png?v=1619977283"),
    ("Dumbbell Fly", "push", "chest", "deltoids",
     "Wide arc motion, stretch the pecs.",
     f"{_SF}/Dumbbell-Fly_119e2918-4241-4f55-bd77-c98a0c76c6c8_600x600.png?v=1612137840"),
    ("Cable Crossover", "push", "chest", "deltoids",
     "Cables crossed in front, constant tension.",
     f"{_SF}/Cable-Crossover_09c90616-2777-47ed-927e-d5987edfce09_600x600.png?v=1612138036"),
    ("Push-up", "push", "chest", "deltoids,triceps",
     "Bodyweight, hands shoulder-width.",
     f"{_SF}/Push-Ups_600x600.png?v=1640121436"),
    ("Overhead Press", "push", "deltoids", "trapezius,triceps",
     "Bar pressed overhead from rack position.",
     f"{_SF}/Standing-Barbell-Shoulder-Press_600x600.png?v=1619977694"),
    ("Dumbbell Shoulder Press", "push", "deltoids", "triceps",
     "Seated or standing, dumbbells to ears.",
     f"{_SF}/Dumbbell-Shoulder-Press_da0aa742-620a-45f7-9277-78137d38ff28_600x600.png?v=1612138495"),
    ("Lateral Raise", "push", "deltoids", "",
     "Arms out to sides to shoulder height.",
     f"{_SF}/Dumbbell-Lateral-Raise_31c81eee-81c4-4ffe-890d-ee13dd5bbf20_600x600.png?v=1612138523"),
    ("Front Raise", "push", "deltoids", "",
     "Raise weight to front, shoulder height.",
     f"{_SF}/Dumbbell-Front-Raise_11804c3c-22d1-4589-a035-e30ad72149f3_600x600.png?v=1612138576"),
    ("Tricep Pushdown", "push", "triceps", "forearm",
     "Cable machine, elbows fixed at sides.",
     f"{_SF}/Triceps-Pressdown_e759437b-6200-4b44-b484-14db770024a4_600x600.png?v=1612136845"),
    ("Skull Crusher", "push", "triceps", "",
     "EZ-bar lowered to forehead, elbows fixed.",
     f"{_SF}/Lying-Triceps-Extension_4affa7a2-9c1c-48f8-8003-3570d7b3a39c_600x600.png?v=1612136744"),
    ("Close-Grip Bench Press", "push", "triceps", "chest",
     "Narrow grip bench, tricep dominant.",
     f"{_SF}/Close-Grip-Bench-Press_28c01bfb-504d-43a6-8264-bd2101d317b9_600x600.png?v=1612137028"),
    ("Dips", "push", "triceps", "chest,deltoids",
     "Parallel bars, lean forward for chest emphasis.",
     f"{_SF}/Parallel-Dip-Bar_600x600.png?v=1619977962"),
    ("Arnold Press", "push", "deltoids", "triceps",
     "Rotation from palms-in to palms-out.",
     f"{_SF}/Dumbbell-Shoulder-Press_da0aa742-620a-45f7-9277-78137d38ff28_600x600.png?v=1612138495"),
    # ── PULL ──────────────────────────────────────────────────────────────
    ("Pull-up", "pull", "upper-back", "biceps",
     "Overhand grip, full range of motion.",
     f"{_SF}/Pull-Up_600x600.png?v=1619977612"),
    ("Chin-up", "pull", "upper-back", "biceps",
     "Underhand grip, more bicep involvement.",
     f"{_SF}/Pull-Up-with-a-Supinated-Grip_600x600.png?v=1619977534"),
    ("Barbell Row", "pull", "upper-back", "biceps,lower-back",
     "Hinged at hips, bar pulled to belly button.",
     f"{_SF}/Barbell-Row_4beb1d94-bac9-4538-9578-2d9cf93ef008_600x600.png?v=1612138201"),
    ("Dumbbell Row", "pull", "upper-back", "biceps",
     "Single-arm, knee and hand on bench.",
     f"{_SF}/Dumbbell-Bent-Over-Row-_Single-Arm_49867db3-f465-4fbc-b359-29cbdda502e2_600x600.png?v=1612138069"),
    ("Seated Cable Row", "pull", "upper-back", "biceps",
     "Cable machine, elbows to sides.",
     f"{_SF}/Seated-Cable-Row_9470fa48-f0d1-40b1-a980-caee9e6f2e53_600x600.png?v=1612138127"),
    ("Lat Pulldown", "pull", "upper-back", "biceps",
     "Wide grip, bar pulled to upper chest.",
     f"{_SF}/Wide-Grip-Pulldown_91fcba9b-47a2-4185-b093-aa542c81c55c_600x600.png?v=1612138105"),
    ("Face Pull", "pull", "upper-back", "deltoids",
     "Rope attachment, pull to face.",
     f"{_SF}/High-Cable-Rear-Delt-Fly_600x600.png?v=1612541996"),
    ("Shrug", "pull", "trapezius", "",
     "Elevate shoulders with heavy load.",
     f"{_SF}/Barbell-Shrug_4f8a4e15-96b9-4595-8e88-635bf83cc8ac_600x600.png?v=1612138751"),
    ("Bicep Curl", "pull", "biceps", "forearm",
     "Standard supinated curl.",
     f"{_SF}/Barbell-Curl_f38580d5-412e-4082-b453-5d319afa94fd_600x600.png?v=1612137128"),
    ("Hammer Curl", "pull", "biceps", "forearm",
     "Neutral grip, targets brachialis.",
     f"{_SF}/Hammer-Curl_da9fea8b-fc81-4a4f-9af1-aea1b85239d7_600x600.png?v=1612137282"),
    ("Preacher Curl", "pull", "biceps", "",
     "Arm braced on angled pad.",
     f"{_SF}/EZ-Barbell-Preacher-Curl_4d449fee-1920-4137-970c-75d4698b268d_600x600.png?v=1612137254"),
    ("Incline Dumbbell Curl", "pull", "biceps", "",
     "Bench at 45°, full stretch at bottom.",
     f"{_SF}/Incline-Dumbbell-Curl_7debf468-cd34-49bc-8933-7f4b087e6cca_600x600.png?v=1612137309"),
    ("Cable Bicep Curl", "pull", "biceps", "forearm",
     "Constant tension through range.",
     f"{_SF}/Straight-Bar-Low-Pulley-Cable-Curl_600x600.png?v=1619978455"),
    ("Straight-Arm Pulldown", "pull", "upper-back", "triceps",
     "Arms straight, lats dominant.",
     f"{_SF}/Straight-Arm-Lat-Pulldown_600x600.png?v=1619977498"),
    ("Rack Pull", "pull", "upper-back", "lower-back,trapezius",
     "Deadlift from knee height.",
     f"{_SF}/Barbell-Deadlift_600x600.png?v=1619977112"),
    # ── LEGS ──────────────────────────────────────────────────────────────
    ("Barbell Back Squat", "legs", "quadriceps", "gluteal,hamstring",
     "Bar on traps, squat to parallel.",
     f"{_SF}/Squat_d752e42d-02ba-4692-b300-c6e67ad5a4f5_600x600.png?v=1612138811"),
    ("Front Squat", "legs", "quadriceps", "gluteal",
     "Bar on front delts, more upright torso.",
     f"{_SF}/Front-Squat_600x600.png?v=1612049397"),
    ("Goblet Squat", "legs", "quadriceps", "gluteal",
     "Dumbbell held at chest.",
     f"{_SF}/Dumbbell-Goblet-Squat_600x600.png?v=1612049778"),
    ("Leg Press", "legs", "quadriceps", "gluteal,hamstring",
     "Machine, feet shoulder-width.",
     f"{_SF}/Leg-Press_f7febd5c-75e5-42f4-9bb4-c938969ce293_600x600.png?v=1612138836"),
    ("Hack Squat", "legs", "quadriceps", "gluteal",
     "Machine, close-stance.",
     f"{_SF}/Hack-Squat_044b3d09-ffa7-4728-b56f-f4fb3c175548_600x600.png?v=1612139060"),
    ("Bulgarian Split Squat", "legs", "quadriceps", "gluteal,hamstring",
     "Rear foot elevated, lunge position.",
     f"{_SF}/Barbell-Bulgarian-Split-Squat_600x600.png?v=1655223749"),
    ("Lunge", "legs", "quadriceps", "gluteal,hamstring",
     "Step forward, lower back knee.",
     f"{_SF}/Lunge_600x600.png?v=1612138903"),
    ("Romanian Deadlift", "legs", "hamstring", "gluteal,lower-back",
     "Hinge with soft knee, bar close to body.",
     f"{_SF}/Barbell-Romanian-Deadlift_34ede1b4-63ac-451d-9536-bbf9942b560c_600x600.png?v=1621162957"),
    ("Leg Curl", "legs", "hamstring", "",
     "Machine, lying or seated.",
     f"{_SF}/Lying-Leg-Curl_203153d8-79dd-4bb9-9125-708aa4327107_600x600.png?v=1612139013"),
    ("Nordic Curl", "legs", "hamstring", "",
     "Partner holds feet, lower under control.",
     f"{_SF}/Glute-Ham-Raise_600x600.png?v=1656405832"),
    ("Hip Thrust", "legs", "gluteal", "hamstring",
     "Bar over hips, upper back on bench.",
     f"{_SF}/Barbell-Hip-Thrust_600x600.png?v=1656402338"),
    ("Glute Bridge", "legs", "gluteal", "",
     "Bodyweight or loaded, floor variation.",
     f"{_SF}/Bodyweight-Glute-Bridge_600x600.png?v=1655224288"),
    ("Deadlift", "legs", "lower-back", "hamstring,gluteal,upper-back",
     "Conventional pull from floor.",
     f"{_SF}/Barbell-Deadlift_600x600.png?v=1619977112"),
    ("Sumo Deadlift", "legs", "lower-back", "gluteal,hamstring,adductors",
     "Wide stance, hands inside legs.",
     f"{_SF}/Barbell-Sumo-Deadlift_600x600.png?v=1619976908"),
    ("Good Morning", "legs", "lower-back", "hamstring",
     "Bar on traps, hinge forward.",
     f"{_SF}/Good-Morning_600x600.png?v=1655224242"),
    ("Calf Raise", "legs", "calves", "",
     "Standing or seated, full range.",
     f"{_SF}/Standing-Calf-Raise_61746b47-98aa-49ee-bb97-5a19562592b9_600x600.png?v=1612137090"),
    ("Seated Calf Raise", "legs", "calves", "",
     "Machine, knee bent targets soleus.",
     f"{_SF}/Seated-Calf-Raise_8c8641b2-10f2-4dc8-9adb-8d80fd1a16d0_600x600.png?v=1612137064"),
    ("Leg Extension", "legs", "quadriceps", "",
     "Machine, full extension.",
     f"{_SF}/Leg-Extension_41d91d3f-4b9c-4374-82e2-1d697ce35fe4_600x600.png?v=1612138862"),
    ("Hip Abduction", "legs", "gluteal", "adductors",
     "Machine or cable, leg out to side.",
     f"{_SF}/Seated-Hip-Abduction-Machine_600x600.png?v=1656405168"),
    ("Adductor Machine", "legs", "adductors", "gluteal",
     "Machine, knees press inward.",
     f"{_SF}/Band-Seated-Hip-Abduction_600x600.png?v=1656404992"),
    # ── CORE ──────────────────────────────────────────────────────────────
    ("Plank", "core", "abs", "lower-back",
     "Forearms on floor, body straight.",
     f"{_SF}/Plank_3a82d566-9cb2-4c20-b301-bc8bd635c4d1_600x600.png?v=1612138431"),
    ("Crunch", "core", "abs", "",
     "Controlled spinal flexion.",
     f"{_SF}/Crunch_f3498d5d-82d9-4a7f-8dee-98a2e55a62f2_600x600.png?v=1612138317"),
    ("Cable Crunch", "core", "abs", "",
     "Kneeling, cable attached overhead.",
     f"{_SF}/Rope-Ab-Pulldown_b808db26-a4f3-4018-8007-5e31da5736dc_600x600.png?v=1612138402"),
    ("Hanging Leg Raise", "core", "abs", "",
     "Hang from bar, raise legs to 90°.",
     f"{_SF}/Hanging-Leg-Raise_36986393-d0a6-494a-981f-4ea06a99b0b5_600x600.png?v=1612138457"),
    ("Ab Rollout", "core", "abs", "lower-back",
     "Wheel or barbell, roll forward and back.",
     f"{_SF}/Plank_3a82d566-9cb2-4c20-b301-bc8bd635c4d1_600x600.png?v=1612138431"),
    ("Russian Twist", "core", "obliques", "abs",
     "Seated rotation with weight.",
     f"{_SF}/Oblique-Crunch_253d0361-395d-443b-8228-aff440c1eee9_600x600.png?v=1612138354"),
    ("Side Plank", "core", "obliques", "abs",
     "Lateral hold, elbow on floor.",
     f"{_SF}/Plank_3a82d566-9cb2-4c20-b301-bc8bd635c4d1_600x600.png?v=1612138431"),
    ("Woodchop", "core", "obliques", "abs",
     "Cable rotation from high to low.",
     f"{_SF}/Rope-Ab-Pulldown_b808db26-a4f3-4018-8007-5e31da5736dc_600x600.png?v=1612138402"),
    ("Back Extension", "core", "lower-back", "gluteal,hamstring",
     "Hyperextension bench, hinge at hips.",
     f"{_SF}/Good-Morning_600x600.png?v=1655224242"),
    ("Dead Bug", "core", "abs", "lower-back",
     "Supine, opposite arm and leg extension.",
     f"{_SF}/Bird-Dog_600x600.png?v=1656401941"),
    # ── CARDIO ────────────────────────────────────────────────────────────
    ("Running", "cardio", "", "",
     "Treadmill or outdoor running.", None),
    ("Cycling", "cardio", "quadriceps", "calves",
     "Bike or stationary cycle.", None),
    ("Rowing Machine", "cardio", "upper-back", "legs",
     "Full-body cardio, drive with legs first.", None),
    ("Jump Rope", "cardio", "calves", "",
     "Double-unders or regular.", None),
    ("Elliptical", "cardio", "quadriceps", "gluteal",
     "Low-impact full-body cardio.", None),
]


def _update_gif_urls(db) -> None:
    """Idempotent: keeps gif_url column in sync with EXERCISES list."""
    updated = 0
    for name, _cat, _pri, _sec, _desc, gif_slug in EXERCISES:
        url = _gif(gif_slug)
        ex = db.query(models.Exercise).filter(models.Exercise.name == name).first()
        if ex and ex.gif_url != url:
            ex.gif_url = url
            updated += 1
    db.commit()
    if updated:
        print(f"Updated {updated} exercise image URLs.")


def seed() -> None:
    db = SessionLocal()
    try:
        if db.query(models.Exercise).count() == 0:
            for name, cat, primary, secondary, desc, gif_slug in EXERCISES:
                db.add(models.Exercise(
                    name=name,
                    category=cat,
                    primary_muscles=primary,
                    secondary_muscles=secondary,
                    description=desc,
                    gif_url=_gif(gif_slug),
                ))
            db.commit()
            print(f"Seeded {len(EXERCISES)} exercises.")
        else:
            print("Exercises already seeded.")
        _update_gif_urls(db)
    finally:
        db.close()


if __name__ == "__main__":
    seed()
