from flask import render_template, request, redirect, url_for, flash
from app import app, db, mail
from flask_mail import Message
from app.models import User
import secrets, emoji
from werkzeug.security import check_password_hash, generate_password_hash

@app.route("/reset_pass", methods=["GET","POST"])
def reset_pass():
    if request.method == "POST":
        email = request.form["email"]
        worried_face = emoji.emojize("\U0001F61F")

        user = User.query.filter_by(email=email).first()

        if user:
            reset_token = secrets.token_urlsafe(16)
            user.reset_token = reset_token
            db.session.commit()

            try:
                reset_link = url_for("reset_password_token", token=reset_token, _external=True)
                msg = Message(
                    "Password Reset Request",
                    sender="citsproject3403@gmail.com",
                    recipients=[email],
                )
                msg.body = f"Dear {user.name_user}, \n\n Please click the following link to reset your password: {reset_link}, \n Please don't share this link with anyone. {worried_face} \n\n Thank you, \n FitTracker Team"
                mail.send(msg)
            except Exception as e:
                print(f"Failed to send password reset email: {e}")

            flash("Password reset link sent.", "success")
        else:
            flash("Email not found.", "error")
        return redirect(url_for("login"))

    return render_template("UsernamePassReset.html")


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password_token(token):
    user = User.query.filter_by(reset_token=token).first()
    if not user:
        flash("Invalid or expired token.", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        password = request.form["password"]
        user.password = generate_password_hash(password, method="pbkdf2:sha256")
        user.reset_token = None
        db.session.commit()
        flash("Password reset successfully.", "success")
        return redirect(url_for("login"))

    return render_template("reset_pass.html", token=token)