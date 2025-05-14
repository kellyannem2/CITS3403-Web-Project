import pytest
from datetime import datetime, date, timedelta

from app import app, db
from app.models import User, Food, MealLog, ExerciseLog, Scoreboard

# --------------------
# Unit tests (pytest)
# --------------------

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    ctx = app.app_context()
    ctx.push()
    db.create_all()
    client = app.test_client()
    yield client
    db.drop_all()
    ctx.pop()

@pytest.fixture
def auth_user(client):
    from werkzeug.security import generate_password_hash
    # Create and login a test user
    user = User(
        username='tester',
        full_name='Tester',
        email='tester@example.com',
        password=generate_password_hash('secret', method='pbkdf2:sha256'),
        is_verified=True
    )
    db.session.add(user)
    db.session.commit()

    rv = client.post(
        '/login',
        data={'username': 'tester', 'password': 'secret'},
        follow_redirects=True
    )
    assert rv.status_code == 200
    return user

# 1: Access control for dashboard
def test_dashboard_requires_login(client):
    rv = client.get('/dashboard', follow_redirects=True)
    assert b'Please log in' in rv.data

# 2: Empty dashboard after login
def test_empty_dashboard(auth_user, client):
    rv = client.get('/dashboard')
    assert b'No logs yet' in rv.data

# 3: Add custom meal successfully
def test_add_custom_meal(auth_user, client):
    dt = datetime.now().strftime('%Y-%m-%dT%H:%M')
    rv = client.post(
        '/dashboard',
        data={
            'meal_date_time': dt,
            'custom_name': 'Banana',
            'custom_calories': '105',
            'submit_custom': 'Add Custom Food'
        },
        follow_redirects=True
    )
    assert b'Logged' in rv.data
    assert b'Banana' in rv.data
    logs = MealLog.query.all()
    assert len(logs) == 1
    assert logs[0].food.name == 'Banana'

# 4: Search meal addition with seeded Food
def test_add_search_meal(auth_user, client):
    food = Food(name='Apple', calories=95, serving_size='1 unit')
    db.session.add(food)
    db.session.commit()
    dt = datetime.now().strftime('%Y-%m-%dT%H:%M')
    rv = client.post(
        '/dashboard',
        data={
            'meal_date_time': dt,
            'search_food': 'Apple',
            'selected_food_id': str(food.id),
            'selected_food_cal': '95',
            'submit_choose': 'Add Selected Food'
        },
        follow_redirects=True
    )
    assert b'Logged' in rv.data
    assert b'Apple' in rv.data
    logs = MealLog.query.all()
    assert len(logs) == 1
    assert logs[0].food.calories == 95

# 5: Missing selection errors
def test_search_without_selection(auth_user, client):
    dt = datetime.now().strftime('%Y-%m-%dT%H:%M')
    rv = client.post(
        '/dashboard',
        data={
            'meal_date_time': dt,
            'search_food': 'Banana',
            'submit_choose': 'Add Selected Food'
        },
        follow_redirects=True
    )
    assert b'Please pick a food' in rv.data
    assert MealLog.query.count() == 0

# 6: Invalid custom meal missing fields
@pytest.mark.parametrize("name,calories", [
    ('', '100'),
    ('Name', ''),
    ('', '')
])
def test_invalid_custom_missing(auth_user, client, name, calories):
    dt = datetime.now().strftime('%Y-%m-%dT%H:%M')
    rv = client.post(
        '/dashboard',
        data={
            'meal_date_time': dt,
            'custom_name': name,
            'custom_calories': calories,
            'submit_custom': 'Add Custom Food'
        },
        follow_redirects=True
    )
    assert b'Provide both a name' in rv.data
    assert MealLog.query.count() == 0

# 7: Invalid datetime format
def test_invalid_datetime_format(auth_user, client):
    rv = client.post(
        '/dashboard',
        data={
            'meal_date_time': 'bad-format',
            'custom_name': 'Test',
            'custom_calories': '50',
            'submit_custom': 'Add Custom Food'
        },
        follow_redirects=True
    )
    assert b'Invalid date/time format' in rv.data
    assert MealLog.query.count() == 0

# 8: API calorie data endpoint requires login
def test_api_calorie_data_requires_login(client):
    rv = client.get('/api/calorie-data')
    assert rv.status_code == 401

# 9: API calorie data returns correct sums
def test_api_calorie_data_values(auth_user, client):
    user = auth_user
    today = date.today()
    f1 = Food(name='X', calories=10, serving_size='')
    f2 = Food(name='Y', calories=20, serving_size='')
    db.session.add_all([f1, f2])
    db.session.flush()
    db.session.add_all([
        MealLog(user_id=user.id, food_id=f1.id, date=today),
        MealLog(user_id=user.id, food_id=f2.id, date=today)
    ])
    db.session.commit()
    rv = client.get('/api/calorie-data')
    data = rv.get_json()
    today_label = today.strftime('%a')
    result = next(item for item in data if item['label'] == today_label)
    assert result['calories'] == 30

# 10: Food search endpoint
def test_api_food_search(client, auth_user):
    f = Food(name='Pear', calories=50, serving_size='')
    db.session.add(f)
    db.session.commit()
    rv = client.get('/api/foods?q=Pe')
    results = rv.get_json()
    assert any(r['name'] == 'Pear' for r in results)