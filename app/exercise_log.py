from flask import request, redirect, url_for, flash, session, render_template, jsonify
from app import app, db
from app.models import User, Exercise, ExerciseLog, Scoreboard, MealLog
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
    default_name = request.form.get("default_exercise", "").strip()
    default_minutes = request.form.get("default_minutes")
    custom_name = request.form.get("custom_name_exe", "").strip()
    custom_minutes = request.form.get("custom_minutes")
    custom_calories = request.form.get("custom_calories_exe")

    try:
        # Case 1: Default exercise (global exercise, user_id = None)
        if "submit_default" in request.form and default_name:
            exercise = Exercise.query.filter_by(user_id=None, name=default_name).first()
            if not exercise:
                # Create the global exercise
                exercise = Exercise(name=default_name, duration_minutes=30, user_id=None)
                db.session.add(exercise)
                db.session.commit()

            duration = float(default_minutes)
            calories = duration * 8  # Basic estimate

        # Case 2: Custom exercise (user-specific)
        elif "submit_custom" in request.form and custom_name:
            # Check if user already added this custom exercise
            exercise = Exercise.query.filter_by(user_id=user_id, name=custom_name).first()
            duration = float(custom_minutes)
            rate = float(custom_calories) / 30
            calories = rate * duration

            if not exercise:
                # Add new custom exercise
                exercise = Exercise(name=custom_name, duration_minutes=duration, user_id=user_id)
                db.session.add(exercise)
                db.session.commit()
            else:
                # Update duration if needed
                exercise.duration_minutes = duration
                db.session.commit()

        else:
            flash("Please fill out all required fields.", "error")
            return redirect(url_for("dashboard"))

        # Log the exercise for today
        log = ExerciseLog(
            user_id=user.id,
            exercise_id=exercise.id,
            duration_minutes=duration,
            calories_burned=calories,
            date=log_date
        )
        db.session.add(log)
        db.session.commit()

        flash("✅ Exercise logged successfully!", "success")
        return redirect(url_for("dashboard"))

    except Exception as e:
        db.session.rollback()
        flash(f"Error logging exercise: {str(e)}", "error")
        return redirect(url_for("dashboard"))
    
@app.route('/search_exercises')
def search_exercises():
    query = request.args.get('q', '').lower()
    user_id = session.get("user_id")

    if not query or not user_id:
        return jsonify([])

    matches = Exercise.query.filter(
        Exercise.name.ilike(f"%{query}%"),
        db.or_(Exercise.user_id == user_id, Exercise.user_id == None)
    ).limit(5).all()

    # Estimate calories burned rate per 30 min
    result = []
    for ex in matches:
        # Assume 8 cal/min as base if we don't have logs
        logs = ExerciseLog.query.filter_by(exercise_id=ex.id).all()
        if logs:
            avg_cals_per_min = sum(l.calories_burned for l in logs) / sum(l.duration_minutes for l in logs)
        else:
            avg_cals_per_min = 8.0

        cal_per_30 = round(avg_cals_per_min * 30, 2)

        result.append({
            "name": ex.name,
            "duration": ex.duration_minutes,
            "calories": cal_per_30
        })

    return jsonify(result)




# Exercise Log Page (week-based)
@app.route('/exercise-log', endpoint='exercise_log')
def exercise_log_page():
    user_id = session.get("user_id")
    if not user_id:
        flash("You are not logged in. Please log in to access this page.", "error")
        return redirect(url_for("login"))

    user = User.query.get(user_id)

    # Get week offset (0=this week, -1=last week, etc.)
    try:
        week_offset = int(request.args.get("week", 0))
    except ValueError:
        week_offset = 0

    # Calculate week range
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    end_of_week = start_of_week + timedelta(days=6)

    # Logs in selected week
    logs = ExerciseLog.query.filter(
        ExerciseLog.user_id == user.id,
        ExerciseLog.date >= start_of_week,
        ExerciseLog.date <= end_of_week
    ).order_by(ExerciseLog.date.desc()).all()

    # Weekly chart
    weekly_results = db.session.query(
        Scoreboard.timestamp,
        func.sum(Scoreboard.total_calories_burned)
    ).filter(
        Scoreboard.user_id == user.id,
        Scoreboard.timestamp >= start_of_week,
        Scoreboard.timestamp <= end_of_week
    ).group_by(Scoreboard.timestamp).all()

    week_data = {r[0].strftime('%a'): float(r[1]) for r in weekly_results}
    labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    chart_data = [week_data.get(day, 0) for day in labels]

    return render_template(
        'exercise_log.html',
        exercise_log=logs,
        chart_data=chart_data,
        date=date,
        week_offset=week_offset,
        start_of_week=start_of_week,
        end_of_week=end_of_week
    )

@app.route("/delete_recent_exercise", methods=["POST"])
def delete_recent_exercise():
    # Fetch the most recent log by highest ID
    today = date.today()
    recent = (
        ExerciseLog.query
        .filter_by(user_id=session.get("user_id"),date=today)
        .order_by(ExerciseLog.id.desc())
        .first()
    )

    if recent:
        db.session.delete(recent)
        db.session.commit()
        flash("Most recent exercise deleted.")
    else:
        flash("No exercise logs to delete.", "warning")

    return redirect(url_for("dashboard"))

@app.route("/delete_recent_meal", methods=["POST"])
def delete_recent_meal():
    user_id = session.get("user_id")
    if not user_id:
        flash("You must be logged in to perform this action.", "error")
        return redirect(url_for("dashboard"))

    today = date.today()

    recent = (
        MealLog.query
        .filter_by(user_id=user_id, date=today)
        .order_by(MealLog.id.desc())
        .first()
    )

    if recent:
        db.session.delete(recent)
        db.session.commit()
        flash("Most recent meal from today deleted.")
    else:
        flash("No meal entries found for today.", "warning")

    return redirect(url_for("dashboard"))