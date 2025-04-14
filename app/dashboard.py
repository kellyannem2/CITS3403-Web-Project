from flask import render_template, session, redirect, url_for, flash
from app import app
from app.models import User

@app.route("/dashboard")
def dashboard():
    if "user_id" in session:
        user = User.query.get(session["user_id"])
        if user:
            return render_template("index.html", user=user)
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