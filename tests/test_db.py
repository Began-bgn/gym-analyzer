import sqlite3

import pytest

import db


def counts():
    conn = db.get_connection()
    try:
        workouts = conn.execute("SELECT COUNT(*) FROM workouts").fetchone()[0]
        sets = conn.execute("SELECT COUNT(*) FROM sets").fetchone()[0]
        return workouts, sets
    finally:
        conn.close()


def test_add_workout_saves_workout_and_sets(temp_db):
    exercise_id = db.add_exercise("Squat", "legs")
    db.add_workout("2026-10-05", "", [(exercise_id, 1, 5, 100.0), (exercise_id, 2, 5, 100.0)])
    assert counts() == (1, 2)


def test_add_workout_rolls_back_when_a_set_is_invalid(temp_db):
    exercise_id = db.add_exercise("Squat", "legs")
    with pytest.raises(sqlite3.IntegrityError):
        db.add_workout("2026-10-05", "", [(exercise_id, 1, 5, 100.0), (exercise_id, 2, 0, 100.0)])
    assert counts() == (0, 0)  # the valid first set was rolled back too