import sqlite3

DB_PATH = "gym.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
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

def get_workout(workout_id):
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT workout_id, workout_date, notes FROM workouts WHERE workout_id = ?",
            (workout_id,),
        ).fetchone()
    finally:
        conn.close()

def list_sets_for_workout(workout_id):
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT e.exercise_name, s.set_nr, s.reps, s.weight "
            "FROM sets s JOIN exercises e ON e.exercise_id = s.exercise_id "
            "WHERE s.workout_id = ? "
            "ORDER BY e.exercise_name, s.set_nr",
            (workout_id,),
        ).fetchall()
    finally:
        conn.close()


        