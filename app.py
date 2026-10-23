import math
import sqlite3
from datetime import datetime
from flask import Flask, abort, redirect, render_template, request, url_for
import db

ROWS = 5

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
    for i in range(ROWS):
        exercise = form.get(f"exercise_{i}", "")
        reps = form.get(f"reps_{i}", "").strip()
        weight = form.get(f"weight_{i}", "").strip()
        if not exercise and not reps and not weight:
            continue
        if not exercise or not reps or not weight:
            raise ValueError(f"Row {i + 1}: fill in exercise, reps and weight.")
        try:
            exercise_id = int(exercise)
            reps = int(reps)
            weight = float(weight)
        except ValueError:
            raise ValueError(f"Row {i + 1}: reps must be a whole number and weight a number.")
        if exercise_id not in valid_ids:
            raise ValueError(f"Row {i + 1}: unknown exercise.")
        if reps <= 0:
            raise ValueError(f"Row {i + 1}: reps must be greater than 0.")
        if not math.isfinite(weight) or weight < 0:
            raise ValueError(f"Row {i + 1}: weight must be 0 or more.")
        counts[exercise_id] = counts.get(exercise_id, 0) + 1
        sets.append((exercise_id, counts[exercise_id], reps, weight))
    if not sets:
        raise ValueError("Add at least one set.")
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
    return render_template("new_workout.html", exercises=exercise_list,
                           error=error, rows=range(ROWS), form=request.form)


@app.route("/workouts/<int:workout_id>")
def workout(workout_id):
    w = db.get_workout(workout_id)
    if w is None:
        abort(404)
    return render_template("workout.html", workout=w,
                           sets=db.list_sets_for_workout(workout_id))