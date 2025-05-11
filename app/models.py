import os
import base64
import secrets
from datetime import date
from sqlalchemy_utils import EncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesGcmEngine
from app import db


def _ensure_encryption_key():
    # Look for an existing KEY in env
    key = os.environ.get('DB_ENCRYPTION_KEY')
    if not key:
        # Generate 32 random bytes, then url-safe base64-encode them
        raw_key = secrets.token_bytes(32)
        key = base64.urlsafe_b64encode(raw_key).decode()
        # Store it for this process
        os.environ['DB_ENCRYPTION_KEY'] = key
        print(f"Generated new DB_ENCRYPTION_KEY: {key}")
    return key

_ENC_KEY = _ensure_encryption_key()

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    team = db.Column(db.String(100), nullable=True)
    profile_img = db.Column(db.String(255), nullable=True) 


    reset_token = db.Column(db.String(100), nullable=True)
    verification_token = db.Column(db.String(100), nullable=True)
    is_verified = db.Column(db.Boolean, default=False)

    email_change_token = db.Column(db.String(64), nullable=True)
    new_email_temp = db.Column(db.String(120), nullable=True)

    usda_api_key = db.Column(
        EncryptedType(
            db.String(128),
            _ENC_KEY,
            AesGcmEngine
        ),
        nullable=True
    )

    # Relationships
    exercises = db.relationship('Exercise', backref='user', lazy=True)
    exercise_logs = db.relationship('ExerciseLog', backref='user', lazy=True)
    meal_logs = db.relationship('MealLog', backref='user', lazy=True)

    shared_logs = db.relationship('Share', 
    foreign_keys='Share.user_id_sender',
    backref='sender',
    lazy=True)

received_logs = db.relationship('Share',
    foreign_keys='Share.user_id_receiver',
    backref='receiver',
    lazy=True)

@property
def meals(self):
    return [log.food for log in self.meal_logs]

class Scoreboard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_calories_burned = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.Date, default=date.today)
    user = db.relationship('User')

class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # NULL if global
    name = db.Column(db.String(100), nullable=False)
    duration_minutes = db.Column(db.Float, nullable=False)

class ExerciseLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)
    duration_minutes = db.Column(db.Float, nullable=False)
    calories_burned = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)

    exercise = db.relationship('Exercise')

class Food(db.Model):
    __tablename__ = "food"

    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(128), unique=True, index=True, nullable=False)
    calories     = db.Column(db.Float,      nullable=False)
    serving_size = db.Column(db.String(64), default='100 g')

class MealLog(db.Model):
    __tablename__ = "meal_log"

    id       = db.Column(db.Integer, primary_key=True)
    user_id  = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    food_id  = db.Column(db.Integer, db.ForeignKey('food.id'), nullable=False)
    date     = db.Column(db.Date,    nullable=False, default=date.today)
    

    food = db.relationship('Food', backref=db.backref('meal_logs', lazy=True))


class Share(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id_sender = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_id_receiver = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, default=date.today)

