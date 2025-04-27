from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

db = SQLAlchemy()
mail = Mail()

app.secret_key = "your_secret_key"  # Change this to a secure secret key
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Database.db"  # SQLite database URI
#the above item is the database URI, which specifies the location of the SQLite database file.
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "citsproject3403@gmail.com"  # verification sender email
app.config["MAIL_PASSWORD"] = "rlxh pqhp zsyo kmib"  # Replace with your email password
mail = Mail(app)

from app import auth , reset_pass , dashboard

from app.models import User #add any other required tables here and the following line would automatically create them


with app.app_context():
    db.create_all()
