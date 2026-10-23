import os
import sqlite3

if os.path.exists("sample.db"):
    os.remove("sample.db")

conn = sqlite3.connect("sample.db")
conn.execute("PRAGMA foreign_keys = ON")
with open("schema.sql") as f:
    conn.executescript(f.read())

with conn:
    conn.execute("INSERT INTO exercises (exercise_name, muscle_group) VALUES ('Squat', 'legs')")
    conn.execute("INSERT INTO exercises (exercise_name, muscle_group) VALUES ('Bench Press', 'chest')")
    SQUAT, BENCH = 1, 2

    workouts = [
        # (date, [(exercise_id, set_nr, reps, weight), ...])
        ("2026-10-05", [(SQUAT, 1, 5, 100), (SQUAT, 2, 5, 100), (BENCH, 1, 8, 60)]),  # Monday
        ("2026-10-11", [(SQUAT, 1, 5, 100)]),                                          # Sunday, same week
        ("2026-10-12", [(SQUAT, 1, 5, 110), (SQUAT, 2, 5, 110), (BENCH, 1, 8, 65)]),   # Monday, new week
        ("2026-10-21", [(SQUAT, 1, 5, 110), (SQUAT, 2, 5, 110),
                        (BENCH, 1, 6, 70), (BENCH, 2, 6, 70)]),                        # Wednesday
    ]
    for workout_date, sets in workouts:
        cursor = conn.execute(
            "INSERT INTO workouts (workout_date, notes) VALUES (?, ?)", (workout_date, "")
        )
        for exercise_id, set_nr, reps, weight in sets:
            conn.execute(
                "INSERT INTO sets (workout_id, exercise_id, set_nr, reps, weight) "
                "VALUES (?, ?, ?, ?, ?)",
                (cursor.lastrowid, exercise_id, set_nr, reps, weight),
            )
conn.close()