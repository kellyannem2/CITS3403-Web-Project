from app import db

class User(db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    name_user = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    reset_token = db.Column(db.String(100), nullable=True)
    verification_token = db.Column(db.String(100), nullable=True)
    is_verified = db.Column(db.Boolean, default=False)


# from flask_sqlalchemy import SQLAlchemy
# from datetime import datetime

# db = SQLAlchemy()

# # ---------------------------
# # User Table
# # ---------------------------
# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), nullable=False, unique=True)
#     email = db.Column(db.String(120), nullable=False, unique=True)
#     password_hash = db.Column(db.String(128), nullable=False)

#     exercises = db.relationship('Exercise', backref='user', lazy=True)
#     meals = db.relationship('Meal', backref='user', lazy=True)
#     exercise_logs = db.relationship('ExerciseLog', backref='user', lazy=True)
#     meal_logs = db.relationship('MealLog', backref='user', lazy=True)

# # ---------------------------
# # Scoreboard Table
# # ---------------------------
# class Scoreboard(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     avg_calories_burned = db.Column(db.Float, nullable=False)
#     timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# # ---------------------------
# # Exercise Definitions Table
# # ---------------------------
# class Exercise(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # NULL if global
#     name = db.Column(db.String(100), nullable=False)
#     calories_per_minute = db.Column(db.Float, nullable=False)

# # ---------------------------
# # Exercise Log Table
# # ---------------------------
# class ExerciseLog(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)
#     duration_minutes = db.Column(db.Float, nullable=False)
#     calories_burned = db.Column(db.Float, nullable=False)
#     date = db.Column(db.Date, nullable=False, default=datetime.utcnow)

#     exercise = db.relationship('Exercise')

# # ---------------------------
# # Meal Definitions Table
# # ---------------------------
# class Meal(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # NULL if global
#     name = db.Column(db.String(100), nullable=False)
#     calories = db.Column(db.Float, nullable=False)

# # ---------------------------
# # Meal Log Table
# # ---------------------------
# class MealLog(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     meal_id = db.Column(db.Integer, db.ForeignKey('meal.id'), nullable=False)
#     date = db.Column(db.Date, nullable=False, default=datetime.utcnow)

#     meal = db.relationship('Meal')