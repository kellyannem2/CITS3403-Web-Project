from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_migrate import Migrate
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# --- Configuration ---
app.secret_key = "your_secret_key"  # Replace with a secure random key
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "citsproject3403@gmail.com"
app.config["MAIL_PASSWORD"] = "rlxh pqhp zsyo kmib"

# --- Extensions ---
db = SQLAlchemy(app)
mail = Mail(app)
migrate = Migrate(app, db)

# --- Import Route Files ---
from app import auth, reset_pass, dashboard, exercise_log  # ✅ <- added exercise_log route file
from app.models import User  # ✅ <- any models you define will be created below

from .forms import MealForm
def inject_meal_form():
    # Now every render_template will have a `form` var available
    return dict(form=MealForm())

# --- DB Initialization ---
with app.app_context():
    db.create_all()