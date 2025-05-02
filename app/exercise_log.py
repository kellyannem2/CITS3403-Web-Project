from flask import request, redirect, url_for, flash, session, render_template
from app import app, db
from app.models import User, Exercise, ExerciseLog, Scoreboard
from datetime import date, timedelta, datetime
from sqlalchemy import func

# Route to log a new exercise (handles both default and custom)
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

    # Get submitted date or fallback
    try:
        log_date_str = request.form.get("log_date")
        log_date = datetime.strptime(log_date_str, "%Y-%m-%d").date()
    except Exception as e:
        flash("Invalid date format.", "error")
        return redirect(url_for("dashboard"))

    # Form inputs
    default_name = request.form.get("default_exercise")
    default_minutes = request.form.get("default_minutes")
    custom_name = request.form.get("custom_name")
    custom_minutes = request.form.get("custom_minutes")
    custom_calories = request.form.get("custom_calories")

    try:
        # Case 1: Default exercise
        if default_name and default_minutes:
            exercise = Exercise.query.filter_by(user_id=None, name=default_name).first()
            if not exercise:
                exercise = Exercise(name=default_name, duration_minutes=30)
                db.session.add(exercise)
                db.session.commit()

            duration = float(default_minutes)
            calories = duration * 8  # Estimate

        # Case 2: Custom exercise
        elif custom_name and custom_minutes and custom_calories:
            duration = float(custom_minutes)
            rate = float(custom_calories) / 30
            calories = rate * duration

            exercise = Exercise(name=custom_name, duration_minutes=duration, user_id=user_id)
            db.session.add(exercise)
            db.session.commit()

        else:
            flash("Please fill out all required fields.", "error")
            return redirect(url_for("dashboard"))

        # Log the exercise with chosen date
        log = ExerciseLog(
            user_id=user.id,
            exercise_id=exercise.id,
            duration_minutes=duration,
            calories_burned=calories,
            date=log_date
        )
        db.session.add(log)

        # Update or create scoreboard entry for that date
        scoreboard = Scoreboard.query.filter_by(user_id=user.id, timestamp=log_date).first()
        if scoreboard:
            scoreboard.total_calories_burned += calories
        else:
            scoreboard = Scoreboard(
                user_id=user.id,
                total_calories_burned=calories,
                timestamp=log_date
            )
            db.session.add(scoreboard)

        db.session.commit()
        flash("Exercise logged and leaderboard updated!", "success")

    except Exception as e:
        db.session.rollback()
        flash("An error occurred while logging the exercise.", "error")
        print("Exercise log error:", e)

    return redirect(url_for("dashboard"))


# Exercise Log Page (full history + weekly chart)
@app.route('/exercise-log', endpoint='exercise_log')  # ✅ Clean endpoint name preserved
def exercise_log_page():  # ✅ Unique function name
    user_id = session.get("user_id")
    if not user_id:
        flash("You are not logged in. Please log in to access this page.", "error")
        return redirect(url_for("login"))

    user = User.query.get(user_id)

    # All logs for user
    all_logs = ExerciseLog.query.filter_by(user_id=user.id).order_by(ExerciseLog.date.desc()).all()

    # Weekly chart data
    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    weekly_results = db.session.query(
        Scoreboard.timestamp,
        func.sum(Scoreboard.total_calories_burned)
    ).filter(
        Scoreboard.user_id == user.id,
        Scoreboard.timestamp >= week_start,
        Scoreboard.timestamp <= today
    ).group_by(Scoreboard.timestamp).all()

    week_data = {r[0].strftime('%a'): float(r[1]) for r in weekly_results}
    labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    chart_data = [week_data.get(day, 0) for day in labels]

    return render_template(
        'exercise_log.html',
        exercise_log=all_logs,
        chart_data=chart_data,
        date=date 
    )
