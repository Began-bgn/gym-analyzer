import sqlite3
from pathlib import Path

import pytest

import db

SCHEMA = (Path(__file__).parent.parent / "schema.sql").read_text()

SQUAT, BENCH = 1, 2
WORKOUTS = [
    # (date, [(exercise_id, set_nr, reps, weight), ...])
    ("2026-10-05", [(SQUAT, 1, 5, 100), (SQUAT, 2, 5, 100), (BENCH, 1, 8, 60)]),  # Monday
    ("2026-10-11", [(SQUAT, 1, 5, 100)]),  # Sunday, same week as 10-05
    ("2026-10-12", [(SQUAT, 1, 5, 110), (SQUAT, 2, 5, 110), (BENCH, 1, 8, 65)]),  # Monday, new week
    ("2026-10-21", [(SQUAT, 1, 5, 110), (SQUAT, 2, 5, 110),
                    (BENCH, 1, 6, 70), (BENCH, 2, 6, 70)]),  # Wednesday
]


@pytest.fixture
def conn():
    """Fresh in-memory database with the schema and known sample data."""
    c = sqlite3.connect(":memory:")
    c.execute("PRAGMA foreign_keys = ON")
    c.row_factory = sqlite3.Row
    c.executescript(SCHEMA)
    with c:
        c.execute("INSERT INTO exercises (exercise_name, muscle_group) VALUES ('Squat', 'legs')")
        c.execute("INSERT INTO exercises (exercise_name, muscle_group) VALUES ('Bench Press', 'chest')")
        for workout_date, sets in WORKOUTS:
            cursor = c.execute(
                "INSERT INTO workouts (workout_date, notes) VALUES (?, ?)", (workout_date, "")
            )
            for exercise_id, set_nr, reps, weight in sets:
                c.execute(
                    "INSERT INTO sets (workout_id, exercise_id, set_nr, reps, weight) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (cursor.lastrowid, exercise_id, set_nr, reps, weight),
                )
    yield c
    c.close()


@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    """Empty database file for db.py, which opens its own connections."""
    path = tmp_path / "test.db"
    setup = sqlite3.connect(path)
    setup.executescript(SCHEMA)
    setup.close()
    monkeypatch.setattr(db, "DB_PATH", str(path))