from flask import render_template, session, redirect, url_for, flash
from app import app, db
from app.models import User, Scoreboard
from datetime import datetime

@app.route("/dashboard")
def dashboard():
    if "user_id" in session:
        user = User.query.get(session["user_id"])
        if user:
            score_board_exists = Scoreboard.query.filter_by(user_id=user.id, timestamp=datetime.utcnow().date()).first()
            total_calories_burnt = sum(log.calories_burned for log in user.exercise_logs)
            
            scoreboard_entries = Scoreboard.query.order_by(Scoreboard.timestamp.desc()).all()
            
            if score_board_exists:
                score_board_exists.total_calories_burned = total_calories_burnt

            else:
                new_entry_scoreboard = Scoreboard(user_id=user.id, total_calories_burned=total_calories_burnt)
                db.session.add(new_entry_scoreboard)
                
            db.session.commit()
                
            user_scoreboard = Scoreboard.query.filter_by(user_id=user.id).first()

            if user_scoreboard and user_scoreboard.team:
                scoreboard_entries = Scoreboard.query.filter_by(team=user_scoreboard.team).order_by(Scoreboard.total_calories_burned.desc()).all()
                
            else:
                scoreboard_entries = Scoreboard.query.filter_by(user_id=user.id).order_by(Scoreboard.timestamp.desc()).all()


            return render_template("index.html", user=user, exercise = user.exercises, meal = user.meals, 
                                exercise_log = user.exercise_logs, meal_log = user.meal_logs, 
                                scoreboard = scoreboard_entries, user_total_calories_burnt = total_calories_burnt)
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
    scoreboard_entries = Scoreboard.query.order_by(Scoreboard.total_calories_burned.desc()).all()
    return render_template('partials/scoreboard.html', scoreboard=scoreboard_entries)