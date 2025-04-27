from flask import render_template, session, redirect, url_for, flash
from app import app, db
from app.models import User, Scoreboard
from datetime import datetime, date

@app.route("/dashboard" )
def dashboard():
    if "user_id" in session:
        user = User.query.get(session["user_id"])
        if user:


            return render_template("index.html", user=user, exercise = user.exercises, meal = user.meals, 
                                exercise_log = user.exercise_logs, meal_log = user.meal_logs)
        else:
            flash("User not found.", "error")
            session.pop("user_id", None)
            return redirect(url_for("login"))
    else:
        flash("You are not logged in. Please log in to access the dashboard.", "error")
        return redirect(url_for("login"))

@app.route('/exercise-log')
def exercise_log():
    return render_template('exercise_log.html')

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

    team_users = User.query.filter_by(team=user.team).all()
    team_user_ids = [u.id for u in team_users]

    team_member_scoreboard = Scoreboard.query.filter(
        Scoreboard.user_id.in_(team_user_ids),
        Scoreboard.timestamp == date.today()
    ).order_by(Scoreboard.total_calories_burned.desc()).all()
    
    return render_template('partials/scoreboard.html', scoreboard=team_member_scoreboard)