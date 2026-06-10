"""
One-off script: scrapes simplyfitness.com to collect exercise illustration URLs.
Run from the backend/ folder with the venv active.
Output: exercise_images.json
"""
import urllib.request, re, json, time, sys

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,*/*;q=0.9',
}

def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.read().decode('utf-8', errors='ignore')

def get_img(slug):
    try:
        html = fetch(f'https://www.simplyfitness.com/pages/{slug}')
        # Primary: find the illustration img by alt text containing "Illustration"
        m = re.search(r'<img[^>]+alt="[^"]*Illustration[^"]*"[^>]+src="([^"]+)"', html)
        if not m:
            # Fallback: any Shopify CDN 600x600 PNG
            m = re.search(r'src="(https://cdn\.shopify\.com/s/files/[^"]+_600x600\.png[^"]*)"', html)
        if m:
            return m.group(1)
        return None
    except Exception as e:
        return f'ERROR:{e}'

# Map: exercise name -> simplyfitness.com page slug
MAPPING = {
    # PUSH
    "Bench Press":             "barbell-bench-press",
    "Incline Bench Press":     "incline-barbell-bench-press",
    "Decline Bench Press":     "barbell-declined-bench-press",
    "Dumbbell Fly":            "dumbbell-fly",
    "Cable Crossover":         "cable-crossover",
    "Push-up":                 "push-ups",
    "Overhead Press":          "standing-barbell-shoulder-press",
    "Dumbbell Shoulder Press": "dumbbell-shoulder-press",
    "Lateral Raise":           "dumbbell-lateral-raise",
    "Front Raise":             "dumbbell-front-raise",
    "Tricep Pushdown":         "triceps-pressdown",
    "Skull Crusher":           "lying-triceps-extension",
    "Close-Grip Bench Press":  "close-grip-bench-press",
    "Dips":                    "parallel-dip-bar",
    "Arnold Press":            "dumbbell-shoulder-press",
    # PULL
    "Pull-up":                 "pull-up",
    "Chin-up":                 "pull-up-with-a-supinated-grip",
    "Barbell Row":             "barbell-row",
    "Dumbbell Row":            "dumbbell-bent-over-row-single-arm",
    "Seated Cable Row":        "seated-cable-row",
    "Lat Pulldown":            "wide-grip-pulldown",
    "Face Pull":               "high-cable-rear-delt-fly",
    "Shrug":                   "barbell-shrug",
    "Bicep Curl":              "barbell-curl",
    "Hammer Curl":             "hammer-curl",
    "Preacher Curl":           "ez-barbell-preacher-curl",
    "Incline Dumbbell Curl":   "incline-dumbbell-curl",
    "Cable Bicep Curl":        "straight-bar-low-pulley-cable-curl",
    "Straight-Arm Pulldown":   "straight-arm-lat-pulldown",
    "Rack Pull":               "barbell-deadlift",
    # LEGS
    "Barbell Back Squat":      "squat",
    "Front Squat":             "front-squat",
    "Goblet Squat":            "dumbbell-goblet-squat",
    "Leg Press":               "leg-press",
    "Hack Squat":              "hack-squat",
    "Bulgarian Split Squat":   "barbell-bulgarian-split-squat",
    "Lunge":                   "lunge",
    "Romanian Deadlift":       "barbell-stiff-leg-deadlift",
    "Leg Curl":                "lying-leg-curl",
    "Nordic Curl":             "glute-ham-raise",
    "Hip Thrust":              "barbell-hip-thrust",
    "Glute Bridge":            "bodyweight-glute-bridge",
    "Deadlift":                "barbell-deadlift",
    "Sumo Deadlift":           "barbell-sumo-deadlift",
    "Good Morning":            "good-morning",
    "Calf Raise":              "standing-calf-raise",
    "Seated Calf Raise":       "seated-calf-raise",
    "Leg Extension":           "leg-extension",
    "Hip Abduction":           "seated-hip-abduction-machine",
    "Adductor Machine":        "band-seated-hip-abduction",
    # CORE
    "Plank":                   "plank",
    "Crunch":                  "crunch",
    "Cable Crunch":            "rope-ab-pulldown",
    "Hanging Leg Raise":       "hanging-leg-raise",
    "Ab Rollout":              "plank",
    "Russian Twist":           "oblique-crunch",
    "Side Plank":              "plank",
    "Woodchop":                "rope-ab-pulldown",
    "Back Extension":          "good-morning",
    "Dead Bug":                "bird-dog",
}

results = {}
for name, slug in MAPPING.items():
    url = get_img(slug)
    results[name] = url
    ok = "OK" if url and not str(url).startswith("ERROR") else str(url)
    print(f"{name:<32} {ok}", flush=True)
    time.sleep(0.3)

out_path = 'exercise_images.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nSaved {len(results)} entries to {out_path}")
