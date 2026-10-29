import click
from datetime import date, datetime, timedelta
import math
import sqlite3
from flask import Flask, abort, redirect, render_template, request, url_for
import db
import review


app = Flask(__name__)

@app.route("/")
def index():
    return redirect(url_for("workouts"))

@app.route("/workouts")
def workouts():
    return render_template("workouts.html", workouts = db.list_workouts())

@app.route("/exercises", methods = ["GET", "POST"])
def exercises():
    error = None
    if request.method == "POST":
        name = request.form["name"].strip()
        muscle_group = request.form["muscle_group"].strip()
        if not name or not muscle_group:
            error = "Name and muscle group are required."
        else:
            try:
                db.add_exercise(name, muscle_group)
                return redirect(url_for("exercises"))
            except sqlite3.IntegrityError:
                error = "That exercise already exists."
    return render_template("exercises.html", exercises = db.list_exercises(), error = error)

def blocks_from_form(form):
    """Group posted fields into [{"exercise": id, "sets": [(reps, weight), ...]}] in page order."""
    ids = sorted(int(k[9:]) for k in form if k.startswith("exercise_") and k[9:].isdigit())
    return [
        {
            "exercise": form.get(f"exercise_{i}", ""),
            "sets": list(zip(form.getlist(f"reps_{i}"), form.getlist(f"weight_{i}"))),
        }
        for i in ids
    ]


def parse_workout(form, valid_ids):
    workout_date = form.get("workout_date", "")
    try:
        parsed = datetime.strptime(workout_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Date must be a real date, like 2026-10-20.")
    if parsed.strftime("%Y-%m-%d") != workout_date:
        raise ValueError("Date must be written as YYYY-MM-DD.")

    notes = form.get("notes", "").strip()
    sets = []
    counts = {}
    for n, block in enumerate(blocks_from_form(form), start=1):
        try:
            exercise_id = int(block["exercise"])
        except ValueError:
            raise ValueError(f"Exercise {n}: pick an exercise.")
        if exercise_id not in valid_ids:
            raise ValueError(f"Exercise {n}: unknown exercise.")
        if not block["sets"]:
            raise ValueError(f"Exercise {n}: add at least one set.")
        for s, (reps, weight) in enumerate(block["sets"], start=1):
            label = f"Exercise {n}, set {s}"
            if not reps.strip() or not weight.strip():
                raise ValueError(f"{label}: fill in reps and weight.")
            try:
                reps = int(reps)
                weight = float(weight)
            except ValueError:
                raise ValueError(f"{label}: reps must be a whole number and weight a number.")
            if reps <= 0:
                raise ValueError(f"{label}: reps must be greater than 0.")
            if not math.isfinite(weight) or weight < 0:
                raise ValueError(f"{label}: weight must be 0 or more.")
            counts[exercise_id] = counts.get(exercise_id, 0) + 1
            sets.append((exercise_id, counts[exercise_id], reps, weight))
    if not sets:
        raise ValueError("Add at least one exercise.")
    return workout_date, notes, sets


@app.route("/workouts/new", methods=["GET", "POST"])
def new_workout():
    exercise_list = db.list_exercises()
    valid_ids = {e["exercise_id"] for e in exercise_list}
    error = None
    if request.method == "POST":
        try:
            workout_date, notes, sets = parse_workout(request.form, valid_ids)
        except ValueError as e:
            error = str(e)
        else:
            db.add_workout(workout_date, notes, sets)
            return redirect(url_for("workouts"))
    blocks = blocks_from_form(request.form) or [{"exercise": "", "sets": [("", "")]}]
    return render_template("new_workout.html", exercises=exercise_list,
                           error=error, blocks=blocks, form=request.form)

@app.route("/workouts/<int:workout_id>")
def workout(workout_id):
    w = db.get_workout(workout_id)
    if w is None:
        abort(404)
    return render_template("workout.html", workout=w,
                           sets=db.list_sets_for_workout(workout_id))

@app.route("/reviews", methods=["GET", "POST"])
def reviews():
    error = None
    conn = db.get_connection()
    try:
        if request.method == "POST":
            try:
                day = datetime.strptime(request.form.get("week_start", ""), "%Y-%m-%d")
            except ValueError:
                error = "Pick a valid date."
            else:
                monday = (day - timedelta(days=day.weekday())).strftime("%Y-%m-%d")
                try:
                    review.generate_review(conn, review.make_client(), monday)
                except review.ReviewError as e:
                    error = str(e)
        all_reviews = review.list_reviews(conn)
    finally:
        conn.close()
    return render_template("reviews.html", reviews=all_reviews, error=error)

def last_full_week_start(today=None):
    today = today or date.today()
    this_monday = today - timedelta(days=today.weekday())
    return (this_monday - timedelta(days=7)).strftime("%Y-%m-%d")


@app.cli.command("generate-review")
def generate_review_command():
    """Create (or reuse) the review for the last full week."""
    week_start = last_full_week_start()
    conn = db.get_connection()
    try:
        text = review.generate_review(conn, review.make_client(), week_start)
    except review.ReviewError as e:
        raise click.ClickException(str(e))
    finally:
        conn.close()
    click.echo(f"Review for week of {week_start}:\n{text}")