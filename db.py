import sqlite3

def get_connection():
    conn = sqlite3.connect("gym.db")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn

def add_workout(workout_date, notes, sets):
    conn = get_connection()
    try:   
        with conn:
            cursor = conn.execute(
                "INSERT INTO workouts (workout_date, notes) VALUES (?, ?)",
                (workout_date, notes),
            )
            workout_id = cursor.lastrowid
            for exercise_id, set_nr, reps, weight in sets:
                conn.execute(
                    "INSERT INTO sets (workout_id, exercise_id, set_nr, reps, weight) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (workout_id, exercise_id, set_nr, reps, weight),
                )
        return workout_id
    finally:
        conn.close()

def add_exercise(name, muscle_group):
    conn = get_connection()
    try:
        with conn:
            cursor = conn.execute(
                        "INSERT INTO exercises (exercise_name, muscle_group) VALUES (?, ?)",
                        (name, muscle_group),
                    )
        return cursor.lastrowid    
    finally:
        conn.close()

def list_exercises():
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT exercise_id, exercise_name, muscle_group "
            "FROM exercises ORDER BY exercise_name"
        ).fetchall()
        return rows
    finally:
         conn.close()


def list_workouts():
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT workout_id, workout_date, notes "
            "FROM workouts ORDER BY workout_date DESC, workout_id DESC"
        ).fetchall()
        return rows
    finally:
        conn.close()


        