import sqlite3
from db import add_exercise, list_exercises, add_workout, list_workouts

squat = add_exercise("Squat", "legs")
bench = add_exercise("Bench Press", "chest")

add_workout("2026-10-20", "good sesion",
            [(squat, 1, 5, 100.0), (squat, 2, 5, 100.0), (bench, 1, 8, 60.0)])

print("after good insert:", len(list_workouts()))

try:
    add_workout("2026-10-21", "bad reps",
                [(squat, 1, 5, 100.0), (squat, 2, 5, 100.0), (squat, 3, 0, 100.0)])
except sqlite3.Error as e:
    print("expected error:", e)
print("after bad reps:", len(list_workouts()))

try:
    add_workout("2026-10-22", "bad exercise", [(999, 1, 5, 100.0)])
except sqlite3.Error as e:
    print("expected error:", e)
print("after fk test:", len(list_workouts()))