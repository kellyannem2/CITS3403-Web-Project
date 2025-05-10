from datetime import datetime, date
from app import db


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

    # Relationships
    exercises = db.relationship('Exercise', backref='user', lazy=True)
    meals = db.relationship('Meal', backref='user', lazy=True)
    exercise_logs = db.relationship('ExerciseLog', backref='user', lazy=True)
    meal_logs = db.relationship('MealLog', backref='user', lazy=True)

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

class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # NULL if global
    name = db.Column(db.String(100), nullable=False)
    calories = db.Column(db.Float, nullable=False)

class MealLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    meal_id = db.Column(db.Integer, db.ForeignKey('meal.id'), nullable=False)
    date = db.Column(db.Date, default=date.today)

    meal = db.relationship('Meal')
    
class Share(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id_sender = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_id_receiver = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, default=date.today)