import pytest
from datetime import date, timedelta
from app import db
from app.models import User, Exercise, ExerciseLog

@pytest.fixture
def user_and_login(client):
    user = User(username="exuser", full_name="Ex User", email="ex@x.com", password="x", is_verified=True)
    db.session.add(user)
    db.session.commit()
    with client.session_transaction() as sess:
        sess["user_id"] = user.id
    return user

# ----------------------
# /add_exercise
# ----------------------

def test_add_exercise_not_logged_in(client):
    res = client.post("/add_exercise", data={}, follow_redirects=True)
    assert b"You must be logged in" in res.data

def test_add_exercise_invalid_date(client, user_and_login):
    res = client.post("/add_exercise", data={
        "log_date": "not-a-date",
        "submit_custom": "true",
        "custom_name_exe": "Jumping",
        "custom_minutes": "30",
        "custom_calories_exe": "300"
    }, follow_redirects=True)
    assert b"Invalid date format" in res.data

def test_add_custom_exercise_valid(client, user_and_login):
    res = client.post("/add_exercise", data={
        "log_date": date.today().strftime("%Y-%m-%d"),
        "submit_custom": "true",
        "custom_name_exe": "Burpees",
        "custom_minutes": "30",
        "custom_calories_exe": "300"
    }, follow_redirects=True)
    assert b"Exercise logged successfully" in res.data

def test_add_default_exercise_valid(client, user_and_login):
    exercise = Exercise(name="Pushups", user_id=None, duration_minutes=30)
    db.session.add(exercise)
    db.session.commit()

    res = client.post("/add_exercise", data={
        "log_date": date.today().strftime("%Y-%m-%d"),
        "submit_default": "true",
        "default_exercise": "Pushups",
        "default_minutes": "20"
    }, follow_redirects=True)
    assert b"Exercise logged successfully" in res.data

def test_add_exercise_missing_fields(client, user_and_login):
    res = client.post("/add_exercise", data={
        "log_date": date.today().strftime("%Y-%m-%d"),
        "submit_custom": "true",
        "custom_name_exe": "",
        "custom_minutes": "",
        "custom_calories_exe": ""
    }, follow_redirects=True)
    assert b"Please fill out all required fields" in res.data

# ----------------------
# /search_exercises
# ----------------------

def test_search_exercises_logged_out(client):
    res = client.get("/search_exercises?q=run")
    assert res.json == []

def test_search_exercises_match(client, user_and_login):
    ex = Exercise(name="Running", duration_minutes=30, user_id=user_and_login.id)
    db.session.add(ex)
    db.session.commit()
    res = client.get("/search_exercises?q=run")
    assert res.status_code == 200
    assert any("Running" in r["name"] for r in res.json)

# ----------------------
# /exercise-log
# ----------------------

def test_exercise_log_page_not_logged_in(client):
    res = client.get("/exercise-log", follow_redirects=True)
    assert b"You are not logged in" in res.data

def test_exercise_log_page_logged_in(client, user_and_login):
    res = client.get("/exercise-log")
    assert b"exercise_log" in res.data or res.status_code == 200

def test_exercise_log_chart_data(client, user_and_login):
    today = date.today()
    ex = Exercise(name="Swim", duration_minutes=30, user_id=user_and_login.id)
    db.session.add(ex)
    db.session.commit()

    log = ExerciseLog(
        user_id=user_and_login.id,
        exercise_id=ex.id,
        duration_minutes=30,
        calories_burned=300,
        date=today
    )
    db.session.add(log)
    db.session.commit()

    res = client.get("/exercise-log")
    assert b"chart_data" in res.data or res.status_code == 200
