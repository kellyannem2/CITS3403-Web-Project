from flask import request, redirect, url_for, flash, session
from app import app, db
from app.models import User, Exercise, ExerciseLog, Scoreboard
from datetime import date

@app.route("/add_exercise", methods=["POST"])
def add_exercise():
    user_id = session.get("user_id")
    if not user_id:
        flash("You must be logged in to log an exercise.", "error")
        return redirect(url_for("login"))

    user = User.query.get(user_id)
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("login"))

    # Get form values
    default_name = request.form.get("default_exercise")
    default_minutes = request.form.get("default_minutes")
    custom_name = request.form.get("custom_name")
    custom_minutes = request.form.get("custom_minutes")
    custom_calories = request.form.get("custom_calories")

    try:
        # Case 1: Default Exercise
        if default_name and default_minutes:
            exercise = Exercise.query.filter_by(user_id=None, name=default_name).first()
            if not exercise:
                exercise = Exercise(name=default_name, duration_minutes=30)
                db.session.add(exercise)
                db.session.commit()

            duration = float(default_minutes)
            calories = duration * 8  # Default estimate: 8 cal/min

        # Case 2: Custom Exercise
        elif custom_name and custom_minutes and custom_calories:
            duration = float(custom_minutes)
            rate = float(custom_calories) / 30
            calories = rate * duration

            exercise = Exercise(name=custom_name, duration_minutes=duration, user_id=user_id)
            db.session.add(exercise)
            db.session.commit()

        else:
            flash("Please fill out the required fields.", "error")
            return redirect(url_for("dashboard"))

        # Create exercise log
        log = ExerciseLog(
            user_id=user.id,
            exercise_id=exercise.id,
            duration_minutes=duration,
            calories_burned=calories,
            date=date.today()
        )
        db.session.add(log)

        # Update or create scoreboard
        scoreboard = Scoreboard.query.filter_by(user_id=user.id, timestamp=date.today()).first()
        if scoreboard:
            scoreboard.total_calories_burned += calories
        else:
            scoreboard = Scoreboard(
                user_id=user.id,
                total_calories_burned=calories,
                timestamp=date.today()
            )
            db.session.add(scoreboard)

        db.session.commit()
        flash("Exercise logged and leaderboard updated!", "success")

    except Exception as e:
        db.session.rollback()
        flash("An error occurred. Please try again.", "error")
        print("Exercise log error:", e)

    return redirect(url_for("dashboard"))
