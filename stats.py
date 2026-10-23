def weekly_volume(conn):
    return conn.execute(
        "SELECT date(w.workout_date, '-6 days', 'weekday 1') AS week_start, "
        "       SUM(s.reps * s.weight) AS volume "
        "FROM workouts w JOIN sets s ON s.workout_id = w.workout_id "
        "GROUP BY week_start "
        "ORDER BY week_start"
    ).fetchall()


def best_set_per_exercise(conn):
    return conn.execute(
        "WITH ranked AS ( "
        "  SELECT e.exercise_name, s.weight, s.reps, "
        "         s.weight * (1 + s.reps / 30.0) AS est_1rm, "
        "         ROW_NUMBER() OVER ( "
        "           PARTITION BY e.exercise_id "
        "           ORDER BY s.weight * (1 + s.reps / 30.0) DESC, s.weight DESC "
        "         ) AS rn "
        "  FROM sets s JOIN exercises e ON e.exercise_id = s.exercise_id "
        ") "
        "SELECT exercise_name, weight, reps, ROUND(est_1rm, 1) AS est_1rm "
        "FROM ranked WHERE rn = 1 "
        "ORDER BY exercise_name"
    ).fetchall()


def week_over_week(conn):
    return conn.execute(
        "WITH weekly AS ( "
        "  SELECT date(w.workout_date, '-6 days', 'weekday 1') AS week_start, "
        "         SUM(s.reps * s.weight) AS volume "
        "  FROM workouts w JOIN sets s ON s.workout_id = w.workout_id "
        "  GROUP BY week_start "
        "), with_prev AS ( "
        "  SELECT week_start, volume, "
        "         LAG(volume) OVER (ORDER BY week_start) AS prev_volume "
        "  FROM weekly "
        ") "
        "SELECT week_start, volume, prev_volume, "
        "       volume - prev_volume AS change, "
        "       ROUND(100.0 * (volume - prev_volume) / NULLIF(prev_volume, 0), 1) AS pct_change "
        "FROM with_prev "
        "ORDER BY week_start"
    ).fetchall()


def personal_records(conn, week_start):
    return conn.execute(
        "WITH weekly_best AS ( "
        "  SELECT date(w.workout_date, '-6 days', 'weekday 1') AS week_start, "
        "         e.exercise_name, "
        "         MAX(s.weight * (1 + s.reps / 30.0)) AS best_1rm "
        "  FROM workouts w "
        "  JOIN sets s ON s.workout_id = w.workout_id "
        "  JOIN exercises e ON e.exercise_id = s.exercise_id "
        "  GROUP BY week_start, e.exercise_id "
        "), compared AS ( "
        "  SELECT cur.exercise_name, cur.best_1rm, "
        "         (SELECT MAX(p.best_1rm) FROM weekly_best p "
        "          WHERE p.exercise_name = cur.exercise_name "
        "            AND p.week_start < cur.week_start) AS previous_best "
        "  FROM weekly_best cur "
        "  WHERE cur.week_start = ? "
        ") "
        "SELECT exercise_name, ROUND(best_1rm, 1) AS best_1rm, "
        "       ROUND(previous_best, 1) AS previous_best "
        "FROM compared "
        "WHERE previous_best IS NOT NULL AND best_1rm > previous_best "
        "ORDER BY exercise_name",
        (week_start,),
    ).fetchall()