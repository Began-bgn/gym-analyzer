import stats


def test_weekly_volume(conn):
    rows = stats.weekly_volume(conn)
    assert [(r["week_start"], r["volume"]) for r in rows] == [
        ("2026-10-05", 1980.0),
        ("2026-10-12", 1620.0),
        ("2026-10-19", 1940.0),
    ]


def test_sunday_belongs_to_the_week_that_started_before_it(conn):
    weeks = {r["week_start"]: r["volume"] for r in stats.weekly_volume(conn)}
    assert "2026-10-11" not in weeks
    assert weeks["2026-10-05"] == 1980.0  # includes the Sunday 10-11 set (500)


def test_best_set_uses_epley_1rm(conn):
    best = {r["exercise_name"]: r for r in stats.best_set_per_exercise(conn)}
    assert best["Squat"]["est_1rm"] == 128.3
    assert best["Bench Press"]["est_1rm"] == 84.0


def test_week_over_week(conn):
    rows = stats.week_over_week(conn)
    assert rows[0]["prev_volume"] is None
    assert rows[0]["pct_change"] is None
    assert rows[1]["change"] == -360.0
    assert rows[1]["pct_change"] == -18.2
    assert rows[2]["change"] == 320.0
    assert rows[2]["pct_change"] == 19.8


def test_personal_records(conn):
    def prs(week):
        return {r["exercise_name"] for r in stats.personal_records(conn, week)}

    assert prs("2026-10-05") == set()  # first week is never a PR
    assert prs("2026-10-12") == {"Squat", "Bench Press"}
    assert prs("2026-10-19") == {"Bench Press"}  # squat equal, not strictly greater


def test_volume_by_muscle_group(conn):
    rows = stats.volume_by_muscle_group(conn, "2026-10-12")
    assert [(r["muscle_group"], r["volume"]) for r in rows] == [
        ("legs", 1100.0),
        ("chest", 520.0),
    ]