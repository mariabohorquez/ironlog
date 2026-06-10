---
description: Generate a workout template for a target muscle group or training style, using exercises from the project database
argument-hint: <target> (e.g. push, legs hypertrophy, upper body)
---

# /gen-workout

Generates a workout template based on a target muscle group or training style.

## Usage
```
/gen-workout <target>
```

Examples:
- `/gen-workout push`
- `/gen-workout legs hypertrophy`
- `/gen-workout upper body 4 exercises`

## Behavior
1. Query the exercise database filtering by the target category/muscle
2. Select 4-6 exercises that cover the target muscles without excessive overlap
3. For each exercise suggest: sets (3-4), rep range (8-12 for hypertrophy, 4-6 for strength), and rest time
4. Output as a ready-to-use workout plan in markdown table format
5. Include a brief note on why each exercise was chosen (primary muscle, movement pattern)
6. If the target is ambiguous, ask for clarification before generating
