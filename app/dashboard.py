from flask import render_template, session, redirect, url_for, flash, request
from app import app, db
from sqlalchemy import func
from app.models import User, Scoreboard, ExerciseLog
from datetime import date, timedelta

@app.route("/dashboard")
def dashboard():
    user_id = session.get("user_id")
    if not user_id:
        flash("You are not logged in. Please log in to access the dashboard.", "error")
        return redirect(url_for("login"))

    user = User.query.get(user_id)
    if not user:
        flash("User not found.", "error")
        session.pop("user_id", None)
        return redirect(url_for("login"))

    # 🔹 Total calories burned today
    total_calories = db.session.query(
        func.sum(ExerciseLog.calories_burned)
    ).filter(
        ExerciseLog.user_id == user.id,
        ExerciseLog.date == date.today()
    ).scalar() or 0

    # 🔹 Today's exercises
    todays_exercises = ExerciseLog.query.filter_by(
        user_id=user.id,
        date=date.today()
    ).all()

    # 🔹 Scoreboard update or creation
    scoreboard_entry = Scoreboard.query.filter_by(
        user_id=user.id,
        timestamp=date.today()
    ).first()

    if scoreboard_entry:
        scoreboard_entry.total_calories_burned = total_calories
    else:
        db.session.add(Scoreboard(
            user_id=user.id,
            total_calories_burned=total_calories,
            timestamp=date.today()
        ))

    db.session.commit()

    # 🔹 Get all teams
    all_teams = db.session.query(User.team).filter(User.team.isnot(None)).distinct().all()
    all_teams = [team[0] for team in all_teams]

    # 🔹 Today's team scoreboard
    team_member_scoreboard = []
    if user.team:
        team_users = User.query.filter_by(team=user.team).all()
        team_user_ids = [u.id for u in team_users]

        team_member_scoreboard = Scoreboard.query.filter(
            Scoreboard.user_id.in_(team_user_ids),
            Scoreboard.timestamp == date.today()
        ).order_by(Scoreboard.total_calories_burned.desc()).all()

    # 🔹 Weekly calories burned chart
    today = date.today()
    week_start = today - timedelta(days=today.weekday())  # Monday

    weekly_results = db.session.query(
        Scoreboard.timestamp,
        func.sum(Scoreboard.total_calories_burned)
    ).filter(
        Scoreboard.user_id == user.id,
        Scoreboard.timestamp >= week_start,
        Scoreboard.timestamp <= today
    ).group_by(Scoreboard.timestamp).all()

    week_data = {record[0].strftime('%a'): float(record[1]) for record in weekly_results}
    labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    chart_data = [week_data.get(day, 0) for day in labels]

    return render_template("index.html",
        user=user,
        exercise=user.exercises,
        meal=user.meals,
        exercise_log=todays_exercises,
        meal_log=user.meal_logs,
        scoreboard=team_member_scoreboard,
        user_total_calories_burnt=total_calories,
        chart_data=chart_data,
        all_teams=all_teams,
        date=date  # ✅ Needed for {{ date.today().isoformat() }} in form
    )


@app.route('/calorie-counter')
def calorie_counter():
    return render_template('calorie_counter.html')


@app.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard.html')


@app.route('/refresh_scoreboard')
def refresh_scoreboard():
    user_id = session.get("user_id")
    if not user_id:
        return "Not logged in", 401

    user = User.query.get(user_id)

    if not user or not user.team:
        return render_template('partials/scoreboard.html', scoreboard=[])

    team_users = User.query.filter_by(team=user.team).all()
    team_user_ids = [u.id for u in team_users]

    if not team_user_ids:
        return render_template('partials/scoreboard.html', scoreboard=[])

    team_member_scoreboard = Scoreboard.query.filter(
        Scoreboard.user_id.in_(team_user_ids),
        Scoreboard.timestamp == date.today()
    ).order_by(Scoreboard.total_calories_burned.desc()).all()

    return render_template('partials/scoreboard.html', scoreboard=team_member_scoreboard)


@app.route('/update_team', methods=['POST'])
def update_team():
    if "user_id" not in session:
        flash("You must be logged in to update your team.", "error")
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    new_team = request.form.get('team') or request.form.get('new_team')

    if not new_team or not new_team.strip():
        flash("Team name cannot be empty.", "warning")
        return redirect(url_for('dashboard'))

    cleaned_team = new_team.strip()

    if user.team == cleaned_team:
        flash(f"You're already in the team: {cleaned_team}", "info")
    else:
        user.team = cleaned_team
        db.session.commit()
        flash(f"You've joined the team: {cleaned_team}", "success")

    return redirect(url_for('dashboard'))
