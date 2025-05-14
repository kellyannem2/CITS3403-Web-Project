# seed.py
from app import app, db
from app.models import User, Exercise, ExerciseLog, Food, MealLog, Scoreboard
from faker import Faker
from werkzeug.security import generate_password_hash
from sqlalchemy import func
from datetime import date, timedelta
import random

fake = Faker()


def seed_database(num_users=50,
                  days_back=30,
                  min_logs=10,
                  max_logs=30):
    with app.app_context():
        # Reset DB
        db.drop_all()
        db.create_all()

        # --- Global Exercises (curated list) ---
        exercise_list = [
            ("Running", 10),
            ("Cycling", 8),
            ("Swimming", 7),
            ("Rowing Machine", 9),
            ("Walking", 4),
            ("Elliptical Trainer", 7),
            ("Jump Rope", 12),
            ("Yoga", 3),
            ("Pilates", 4),
            ("HIIT", 11),
            ("Squats", 6),
            ("Push-ups", 8),
            ("Bench Press", 6),
            ("Deadlift", 6),
            ("Pull-ups", 7),
            ("Lunges", 5),
            ("Stair Climber", 8),
            ("Burpees", 10),
            ("Plank", 3),
            ("Mountain Climbers", 9)
        ]
        all_exercises = []
        for name, rate in exercise_list:
            ex = Exercise(name=name, duration_minutes=rate)
            db.session.add(ex)
            all_exercises.append(ex)

        # --- Global Foods (curated list) ---
        food_list = [
            ("Apple", 95),
            ("Banana", 105),
            ("Chicken Breast (100g)", 165),
            ("Almonds (30g)", 170),
            ("Brown Rice (100g)", 112),
            ("Oatmeal (100g)", 68),
            ("Greek Yogurt (100g)", 59),
            ("Walnuts (30g)", 200),
            ("Broccoli (100g)", 55),
            ("Salmon (100g)", 208),
            ("Sweet Potato (100g)", 86),
            ("Quinoa (100g)", 120),
            ("Blueberries (100g)", 57),
            ("Avocado (half)", 160),
            ("Turkey Sandwich", 250),
            ("Egg (large)", 78),
            ("Spinach (100g)", 23),
            ("Carrot (100g)", 41),
            ("Hummus (30g)", 70),
            ("Protein Shake", 150)
        ]
        all_foods = []
        for name, cals in food_list:
            fd = Food(name=name, calories=cals)
            db.session.add(fd)
            all_foods.append(fd)

        db.session.commit()

        # --- Create Users ---
        teams = [
            "Red Dragons", "Blue Sharks",
            "Green Giants", "Yellow Tigers",
            "Silver Wolves", "Golden Eagles"
        ]
        users = []
        for _ in range(num_users):
            user = User(
                username=fake.unique.user_name(),
                full_name=fake.name(),
                email=fake.unique.email(),
                password=generate_password_hash("Password!23"),
                is_verified=True,
                team=random.choice(teams),
                profile_img=fake.image_url(width=100, height=100)
            )
            db.session.add(user)
            users.append(user)
        db.session.commit()

        # --- Generate Logs & Scoreboards ---
        start_date = date.today() - timedelta(days=days_back)
        for user in users:
            # Exercise Logs
            for _ in range(random.randint(min_logs, max_logs)):
                ex = random.choice(all_exercises)
                # duration in minutes, calories based on rate
                duration = random.uniform(15, 90)
                calories = round(duration * ex.duration_minutes / 60, 2)
                log_date = start_date + timedelta(days=random.randint(0, days_back))

                ex_log = ExerciseLog(
                    user_id=user.id,
                    exercise_id=ex.id,
                    duration_minutes=round(duration, 1),
                    calories_burned=calories,
                    date=log_date
                )
                db.session.add(ex_log)

            # Meal Logs
            for _ in range(random.randint(min_logs, max_logs)):
                fd = random.choice(all_foods)
                log_date = start_date + timedelta(days=random.randint(0, days_back))
                ml = MealLog(
                    user_id=user.id,
                    food_id=fd.id,
                    date=log_date
                )
                db.session.add(ml)

            db.session.commit()

            # Today's scoreboard entry
            today_burned = db.session.query(
                func.sum(ExerciseLog.calories_burned)
            ).filter_by(user_id=user.id, date=date.today()).scalar() or 0
            sb = Scoreboard(
                user_id=user.id,
                total_calories_burned=round(today_burned, 2),
                timestamp=date.today()
            )
            db.session.add(sb)
        db.session.commit()

        print(f"✅ Seeded {num_users} users, {len(all_exercises)} exercises, {len(all_foods)} foods over the past {days_back} days.")


if __name__ == '__main__':
    seed_database()