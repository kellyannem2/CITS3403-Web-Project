from app import app
from app import db , mail
from flask_mail import Message
from werkzeug.security import check_password_hash, generate_password_hash
from flask import render_template, request, redirect, url_for, session, flash
import secrets, emoji
from app.models import User

@app.route("/")
def root():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()

        if not user:
            flash("New User.", "error")
            return redirect(url_for("signup"))
        else:
            if check_password_hash(user.password, password):
                if user.is_verified:
                    session["user_id"] = user.id
                    flash("Logged in successfully!", "success")
                    return redirect(url_for("dashboard"))
                else:
                    flash("User not verified. Please check your email.", "error")
            else:
                flash("Invalid credentials.", "error")

    return render_template("Login.html")


@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        full_name = request.form["first_name"] + " " + request.form["last_name"]

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("signup"))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists.", "error")
            return redirect(url_for("login"))

        try:
            hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
            verification_token = secrets.token_urlsafe(16)
            new_user = User(
                email=email, username=username, password=hashed_password,
                full_name=full_name, verification_token=verification_token
            )
            db.session.add(new_user)
            db.session.commit()

            smiley_face = emoji.emojize("\U0001F642")
            verification_link = url_for("verify_email", token=verification_token, _external=True)
            msg = Message("Email Verification", sender="citsproject3403@gmail.com", recipients=[email])
            msg.body = f"Dear {full_name}, \n\nPlease click the following link to verify your email: {verification_link} \n We welcome you to our website, {smiley_face} \n\n Thank you again, \n FitTracker Team"
            mail.send(msg)

            flash("Account created! Check your email.", "success")
            return redirect(url_for("login"))

        except Exception:
            db.session.rollback()
            flash("An error occurred. Please try again.", "error")
            return redirect(url_for("signup"))

    return render_template("signup.html")


@app.route("/verify_email/<token>")
def verify_email(token):
    user = User.query.filter_by(verification_token=token).first()
    if user:
        user.is_verified = True
        user.verification_token = None
        db.session.commit()
        flash("Email verified!", "success")
        return redirect(url_for("login"))
    else:
        flash("Invalid or expired link.", "error")
        return redirect(url_for("signup"))

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))