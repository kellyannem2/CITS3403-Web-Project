from flask import request, redirect, url_for, flash, session, render_template
from app import app, db
from app.models import User, Exercise, ExerciseLog, Scoreboard
from datetime import date, timedelta, datetime
from sqlalchemy import func


@app.route('/shared_logs')
def share_logs():
    return render_template('share_logs.html')
