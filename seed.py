from app import app, db
from app.models import User, Exercise, ExerciseLog, Meal, MealLog, Scoreboard
from faker import Faker
from werkzeug.security import generate_password_hash
from datetime import date, timedelta
import random

fake = Faker()

with app.app_context():
    db.drop_all()
    db.create_all()

    teams = ["Red Dragons", "Blue Sharks", "Green Giants", "Yellow Tigers"]

    users = []
    for _ in range(5):   # Create 5 random users
        user = User(
            username=fake.user_name(),
            full_name=fake.name(),
            email=fake.email(),
            password=generate_password_hash("password123"),
            is_verified=True
        )
        db.session.add(user)
        users.append(user)
    db.session.commit()

    for user in users:
        # Create random Exercises & Meals for each user
        exercises = []
        meals = []

        for _ in range(3):
            ex = Exercise(name=fake.word().capitalize(), duration_minutes=random.randint(20, 60), user_id=user.id)
            meal = Meal(name=fake.word().capitalize(), calories=random.randint(300, 900), user_id=user.id)
            ex_null = Exercise(name=fake.word().capitalize(), duration_minutes=random.randint(20, 60), user_id=None)
            meal_null = Meal(name=fake.word().capitalize(), calories=random.randint(300, 900), user_id=None)
            db.session.add(ex_null)
            db.session.add(meal_null)
            db.session.add(ex)
            db.session.add(meal)
            
            exercises.append(ex)
            meals.append(meal)
            exercises.append(ex_null)
            meals.append(meal_null)
            

        db.session.commit()

        # Generate Exercise Logs
        for _ in range(5):
            chosen_ex = random.choice(exercises)
            duration = random.randint(15, 90)
            calories_burned = round(duration * random.uniform(5, 12), 2)
            log_date = date.today() - timedelta(days=random.randint(0, 7))

            ex_log = ExerciseLog(
                user_id=user.id,
                exercise_id=chosen_ex.id,
                duration_minutes=duration,
                calories_burned=calories_burned,
                date=log_date
            )
            db.session.add(ex_log)

        # Generate Meal Logs
        for _ in range(5):
            chosen_meal = random.choice(meals)
            log_date = date.today() - timedelta(days=random.randint(0, 7))

            meal_log = MealLog(
                user_id=user.id,
                meal_id=chosen_meal.id,
                date=log_date
            )
            db.session.add(meal_log)

        # Create Scoreboard Entry
        total_burned = sum(log.calories_burned for log in user.exercise_logs)
        scoreboard_entry = Scoreboard(
            user_id=user.id,
            total_calories_burned=round(total_burned, 2),
            timestamp=date.today(),
            team=random.choice(teams)
        )
        db.session.add(scoreboard_entry)

    db.session.commit()
    print("Database successfully seeded with random dummy data!")
