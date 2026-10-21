

CREATE TABLE exercises
(
exercise_id INTEGER PRIMARY KEY,
exercise_name TEXT NOT NULL UNIQUE,
muscle_group TEXT NOT NULL
);

CREATE TABLE workouts
(
workout_id INTEGER PRIMARY KEY,
workout_date TEXT NOT NULL, 
notes TEXT
);

CREATE TABLE sets
(
workout_id INTEGER NOT NULL,
exercise_id INTEGER NOT NULL,
set_id INTEGER PRIMARY KEY,
set_nr INTEGER NOT NULL CHECK (set_nr > 0),
reps INTEGER NOT NULL CHECK (reps > 0),
weight REAL NOT NULL CHECK (weight >= 0),
FOREIGN KEY (workout_id) REFERENCES workouts(workout_id),
FOREIGN KEY (exercise_id) REFERENCES exercises(exercise_id),
UNIQUE (workout_id, exercise_id, set_nr)
);


CREATE TABLE weekly_reviews
(
review_id INTEGER PRIMARY KEY NOT NULL,
weekly_start_date TEXT NOT NULL UNIQUE,
review TEXT NOT NULL,
created_at TEXT DEFAULT CURRENT_TIMESTAMP NOT NULL
);

