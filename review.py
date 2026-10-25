import os

from dotenv import load_dotenv
from groq import Groq, APIError

import stats

load_dotenv()
MODEL = "openai/gpt-oss-120b"


class ReviewError(Exception):
    pass


def make_client():
    key = os.environ.get("GROQ_API_KEY")
    if not key or key == "placeholder":
        raise ReviewError("GROQ_API_KEY is not set in .env")
    return Groq(api_key=key)

def get_stored_review(conn, week_start):
    row = conn.execute(
        "SELECT review FROM weekly_reviews WHERE weekly_start_date = ?", (week_start,)
    ).fetchone()
    return row["review"] if row else None


def list_reviews(conn):
    return conn.execute(
        "SELECT weekly_start_date, review FROM weekly_reviews "
        "ORDER BY weekly_start_date DESC"
    ).fetchall()


def build_prompt(conn, week_start):
    by_muscle = stats.volume_by_muscle_group(conn, week_start)
    if not by_muscle:
        raise ReviewError("No workouts logged for that week.")
    lines = [f"Training week starting {week_start}.", "Volume by muscle group (kg):"]
    lines += [f"- {r['muscle_group']}: {r['volume']:.0f}" for r in by_muscle]

    for r in stats.week_over_week(conn):
        if r["week_start"] == week_start and r["prev_volume"] is not None:
            lines.append(
                f"Total volume {r['volume']:.0f}, change vs last week "
                f"{r['change']:+.0f} ({r['pct_change']}%)."
            )
    prs = stats.personal_records(conn, week_start)
    if prs:
        lines.append("Personal records (estimated 1RM, kg):")
        lines += [
            f"- {r['exercise_name']}: {r['best_1rm']} (previous best {r['previous_best']})"
            for r in prs
        ]
    lines.append(
        "Write a short, honest, encouraging review (max 120 words, plain text, "
        "no markdown): what went well, what to watch, one suggestion for next week. "
        "Use only the numbers above. Do not invent exercises or data that is not listed."
    )
    return "\n".join(lines)


def generate_review(conn, client, week_start):
    stored = get_stored_review(conn, week_start)
    if stored is not None:
        return stored

    prompt = build_prompt(conn, week_start)
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
    except APIError as e:
        raise ReviewError(f"Groq API call failed: {e}") from e

    text = response.choices[0].message.content
    if not text:
        raise ReviewError("Groq returned no text.")

    with conn:
        conn.execute(
            "INSERT INTO weekly_reviews (weekly_start_date, review) VALUES (?, ?)",
            (week_start, text),
        )
    return text