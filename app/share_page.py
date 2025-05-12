from flask import request, redirect, url_for, flash, session, render_template
from app import app, db
from app.models import User, Exercise, ExerciseLog, Scoreboard
from datetime import date, timedelta, datetime
from sqlalchemy import func

'''
@app.route('/share_snapshot', methods=['POST'])
def share_snapshot():
    user_id = session.get("user_id")
    if not user_id:
        flash("You must be logged in to share.", "error")
        return redirect(url_for("login"))

    recipient_username = request.form.get("recipient_username")
    if not recipient_username:
        flash("Please enter a username to share with.", "error")
        return redirect(url_for("dashboard"))

    # Get users
    sender = User.query.get(user_id)
    recipient = User.query.filter_by(username=recipient_username).first()

    if not recipient:
        flash("User not found.", "error")
        return redirect(url_for("dashboard"))

    # Create share record
    share = Share(
        user_id_sender=sender.id,
        user_id_receiver=recipient.id
    )
    db.session.add(share)
    db.session.commit()

    flash(f"Shared successfully with {recipient.username}!", "success")
    return redirect(url_for("dashboard"))

'''