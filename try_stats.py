import sqlite3
import stats

conn = sqlite3.connect("sample.db")
conn.row_factory = sqlite3.Row

print("weekly volume")
for row in stats.weekly_volume(conn):
    print(" ", dict(row))

print("best set per exercise")
for row in stats.best_set_per_exercise(conn):
    print(" ", dict(row))

print("week over week")
for row in stats.week_over_week(conn):
    print(" ", dict(row))

for week in ("2026-10-05", "2026-10-12", "2026-10-19"):
    print("personal records, week of", week)
    for row in stats.personal_records(conn, week):
        print(" ", dict(row))

conn.close()