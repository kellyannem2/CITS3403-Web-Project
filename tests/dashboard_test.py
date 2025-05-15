import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from datetime import datetime, date, timedelta
from app import app, db
from app.models import User, Food, MealLog, ExerciseLog

@pytest.fixture
def user_and_login(client):
    user = User(username="testuser", full_name="Test User", email="test@x.com", password="x", is_verified=True)
    db.session.add(user)
    db.session.commit()
    with client.session_transaction() as sess:
        sess["user_id"] = user.id
    return user

# -----------------------
# /dashboard POST routes
# -----------------------

def test_dashboard_invalid_date(client, user_and_login):
    res = client.post("/dashboard", data={"meal_date_time": "bad-date"}, follow_redirects=True)
    assert res.status_code == 200

def test_dashboard_unknown_action(client, user_and_login):
    res = client.post("/dashboard", data={"meal_date_time": datetime.now().isoformat(), "invalid_btn": "clicked"}, follow_redirects=True)
    assert b"Unknown action" in res.data

def test_dashboard_missing_custom_fields(client, user_and_login):
    res = client.post("/dashboard", data={
        "meal_date_time": datetime.now().isoformat(),
        "submit_custom": True,
        "custom_name": "",
        "custom_calories": ""
    }, follow_redirects=True)
    assert b"Provide both a name" in res.data

# -----------------------
# /calorie-counter POST
# -----------------------

def test_calorie_counter_invalid_user_id(client):
    with client.session_transaction() as sess:
        sess["user_id"] = "bad"
    res = client.get("/calorie-counter")
    assert res.status_code == 400

def test_calorie_counter_invalid_date(client, user_and_login):
    res = client.post("/calorie-counter", data={"meal_date_time": "bad"}, follow_redirects=True)
    assert b"Invalid date/time format" in res.data

# -----------------------
# /update_team
# -----------------------

def test_update_team_blank(client, user_and_login):
    res = client.post("/update_team", data={"team": ""}, follow_redirects=True)
    assert b"Team name cannot be empty" in res.data

def test_update_team_same_name(client, user_and_login):
    user_and_login.team = "Kookaburras"
    db.session.commit()
    res = client.post("/update_team", data={"team": "Kookaburras"}, follow_redirects=True)
    assert b"already in the team" in res.data

# -----------------------
# /user/<id>
# -----------------------

def test_user_detail_unauthenticated(client):
    res = client.get("/user/1", follow_redirects=True)
    assert b"Please log in to view user profiles" in res.data

def test_user_detail_authenticated(client, user_and_login):
    res = client.get(f"/user/{user_and_login.id}")
    assert res.status_code == 200
    assert b"testuser" in res.data  


# -----------------------
# /refresh_scoreboard
# -----------------------

def test_api_calorie_data_not_logged_in(client):
    with client.session_transaction() as sess:
        sess.clear()
    res = client.get("/api/calorie-data")
    assert res.status_code == 401


def test_refresh_scoreboard_no_team(client, user_and_login):
    res = client.get("/refresh_scoreboard")
    assert res.status_code == 200
    assert b"scoreboard" in res.data

# -----------------------
# /api/calorie-data
# -----------------------

def test_api_calorie_data_not_logged_in(client):
    res = client.get("/api/calorie-data")
    assert res.status_code == 401

def test_api_calorie_data_invalid_user_id(client):
    with client.session_transaction() as sess:
        sess["user_id"] = "???"
    res = client.get("/api/calorie-data")
    assert res.status_code == 400

def test_api_calorie_data_with_logs(client, user_and_login):
    food = Food(name="Toast", calories=300, serving_size="2 slices")
    db.session.add(food)
    db.session.commit()
    monday = date.today() - timedelta(days=date.today().weekday())
    db.session.add(MealLog(user_id=user_and_login.id, food_id=food.id, date=monday))
    db.session.commit()
    res = client.get("/api/calorie-data")
    assert any(item["label"] == "Mon" and item["calories"] >= 300 for item in res.json)

# -----------------------
# /api/foods
# -----------------------

def test_api_foods_query_too_short(client):
    res = client.get("/api/foods?q=x")
    assert res.json == []
