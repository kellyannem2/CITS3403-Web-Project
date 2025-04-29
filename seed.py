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
    for _ in range(10):   # Create 5 random users
        user = User(
            username=fake.user_name(),
            full_name=fake.name(),
            email=fake.email(),
            password=generate_password_hash("password123"),
            is_verified=True,
            team=random.choice(teams)   # Assign team here
        )
        db.session.add(user)
        users.append(user)

    db.session.commit()  # Commit users first to get their IDs

    for user in users:
        # Create random Exercises & Meals (3 custom + 3 global)
        exercises = []
        meals = []

        for _ in range(5):
            # Custom Exercise & Meal
            ex = Exercise(name=fake.word().capitalize(), duration_minutes=random.randint(20, 60), user_id=user.id)
            meal = Meal(name=fake.word().capitalize(), calories=random.randint(300, 900), user_id=user.id)
            # Global Exercise & Meal
            ex_null = Exercise(name=fake.word().capitalize(), duration_minutes=random.randint(20, 60), user_id=None)
            meal_null = Meal(name=fake.word().capitalize(), calories=random.randint(300, 900), user_id=None)
            
            db.session.add_all([ex, meal, ex_null, meal_null])
            exercises.extend([ex, ex_null])
            meals.extend([meal, meal_null])

        db.session.commit()  # Commit exercises and meals to get IDs

        # Generate Exercise Logs
        for _ in range(10):
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
        for _ in range(10):
            chosen_meal = random.choice(meals)
            log_date = date.today() - timedelta(days=random.randint(0, 7))

            meal_log = MealLog(
                user_id=user.id,
                meal_id=chosen_meal.id,
                date=log_date
            )
            db.session.add(meal_log)

        db.session.commit()  # Commit logs before calculating total calories

        # Calculate total calories burned **for today only**
        today_burned = db.session.query(
            db.func.sum(ExerciseLog.calories_burned)
        ).filter_by(user_id=user.id, date=date.today()).scalar() or 0

        # Create Scoreboard Entry
        scoreboard_entry = Scoreboard(
            user_id=user.id,
            total_calories_burned=round(today_burned, 2),
            timestamp=date.today()
        )
        db.session.add(scoreboard_entry)

    db.session.commit()
    print("✅ Database successfully seeded with random dummy data!")
