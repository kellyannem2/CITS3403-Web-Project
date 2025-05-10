from app import app
from app import db, mail
from flask_mail import Message
from werkzeug.security import check_password_hash, generate_password_hash
from flask import render_template, request, redirect, url_for, session, flash
import secrets, emoji
from app.models import User
import os

@app.route("/")
def root():
    return render_template("pre_login.html")

@app.route("/login", methods=["GET", "POST"])
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

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        full_name = request.form["firstNameInput"] + " " + request.form["lastNameInput"]

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

            smiley_face = emoji.emojize(":slightly_smiling_face:")
            verification_link = url_for("verify_email", token=verification_token, _external=True)
            msg = Message("Email Verification", sender="citsproject3403@gmail.com", recipients=[email])
            msg.body = f"Dear {full_name}, \n\nPlease click the following link to verify your email: {verification_link} \nWe welcome you to our website, {smiley_face} \n\nThank you again, \nFitTracker Team"
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
    
@app.route('/account')
def account():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Force login if not logged in

    user_id = session['user_id']
    user = User.query.get(user_id)

    return render_template('account.html', user=user)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        action = request.form.get('action')

        # === EMAIL CHANGE REQUEST ===
        if action == 'request_email_change':
            new_email = request.form['new_email'].strip()
            current_pw = request.form['current_password']
            # verify password
            if not check_password_hash(user.password, current_pw):
                flash('Current password is incorrect.', 'error')
                return redirect(url_for('account'))

            # generate a token and send verification to new address
            token = secrets.token_urlsafe(16)
            user.email_change_token = token
            user.new_email_temp = new_email
            db.session.commit()

            # send verification link to NEW email
            link = url_for('verify_email_change', token=token, _external=True)
            msg = Message('Confirm Your New Email',
                          sender='citsproject3403@gmail.com',
                          recipients=[new_email])
            msg.body = (f"Hi {user.full_name},\n\n"
                        f"Please click to confirm your new email address:\n{link}\n\n"
                        "If you did not request this, please ignore.")
            mail.send(msg)

            # notify old email
            notice = Message('Your email was changed?',
                             sender='citsproject3403@gmail.com',
                             recipients=[user.email])
            notice.body = (f"Hi {user.full_name},\n\n"
                           f"A request was made to change your FitTrack email to {new_email}.\n"
                           "If this wasn’t you, please contact support immediately.")
            mail.send(notice)

            flash('Verification sent to your new email. Check it to confirm.', 'info')
            return redirect(url_for('account'))

        # === PASSWORD CHANGE ===
        elif action == 'change_password':
            current_pw = request.form['current_password']
            new_pw     = request.form['password']
            confirm_pw = request.form['confirm_password']

            if not check_password_hash(user.password, current_pw):
                flash('Current password is incorrect.', 'error')
            elif new_pw != confirm_pw:
                flash('New passwords do not match.', 'error')
            else:
                user.password = generate_password_hash(new_pw)
                db.session.commit()
                flash('Password updated successfully!', 'success')

            return redirect(url_for('account'))
        # === USDA API KEY ===
        elif action == 'update_usda_key':
            current_pw = request.form.get('current_password', '')
            new_key    = request.form.get('usda_api_key', '').strip() or None

            # verify the current password
            if not check_password_hash(user.password, current_pw):
                flash('Current password is incorrect.', 'error')
            else:
                user.usda_api_key = new_key
                db.session.commit()
                if new_key:
                    flash('USDA API key updated successfully!', 'success')
                else:
                    flash('USDA API key cleared.', 'info')

            return redirect(url_for('account'))

    return render_template('account.html', user=user)


@app.route('/verify_email_change/<token>')
def verify_email_change(token):
    user = User.query.filter_by(email_change_token=token).first()
    if not user:
        flash('Invalid or expired email change link.', 'error')
        return redirect(url_for('account'))

    # finalize the swap
    user.email = user.new_email_temp
    user.new_email_temp = None
    user.email_change_token = None
    db.session.commit()

    flash('Your email address has been updated!', 'success')
    return redirect(url_for('account'))

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return ('.' in filename
            and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS)

@app.route('/upload_avatar', methods=['POST'])
def upload_avatar():
    # require login
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])

    file = request.files.get('avatar')
    if not file or file.filename == '':
        flash('No file selected.', 'error')
        return redirect(url_for('account'))
    if not allowed_file(file.filename):
        flash('Please upload an image file (png/jpg/jpeg/gif/webp).', 'error')
        return redirect(url_for('account'))

    # secure & versioned filename: user_<id>.<ext>
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"user_{user.id}.{ext}"

    # ensure the directory exists
    save_dir = os.path.join(app.static_folder, 'images', 'user_profiles')
    os.makedirs(save_dir, exist_ok=True)

    # save the file
    file_path = os.path.join(save_dir, filename)
    file.save(file_path)

    # update user record
    # store relative path under static/, e.g. 'images/user_profiles/user_3.png'
    user.profile_img = os.path.join('images', 'user_profiles', filename)
    db.session.commit()

    flash('Profile picture updated!', 'success')
    return redirect(url_for('account'))

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))