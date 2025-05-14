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
    with app.test_client() as c:
        with app.app_context():
            db.create_all()
        yield c
        with app.app_context():
            db.drop_all()

@pytest.fixture
def auth_user(client):
    from werkzeug.security import generate_password_hash
    # Create and login a test user
    user = User(
        username='tester', full_name='Tester', email='tester@example.com',
        password=generate_password_hash('secret'), is_verified=True
    )
    db.session.add(user)
    db.session.commit()
    rv = client.post('/login', data={'username':'tester','password':'secret'}, follow_redirects=True)
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
    rv = client.post('/dashboard', data={
        'meal_date_time': dt,
        'custom_name': 'Banana',
        'custom_calories': '105',
        'submit_custom': 'Add Custom Food'
    }, follow_redirects=True)
    assert b'Logged "Banana"' in rv.data
    logs = MealLog.query.all()
    assert len(logs) == 1
    assert logs[0].food.name == 'Banana'

# 4: Search meal addition with seeded Food
def test_add_search_meal(auth_user, client):
    # seed a food record
    food = Food(name='Apple', calories=95, serving_size='1 unit')
    db.session.add(food)
    db.session.commit()
    dt = datetime.now().strftime('%Y-%m-%dT%H:%M')
    rv = client.post('/dashboard', data={
        'meal_date_time': dt,
        'search_food': 'Apple',
        'selected_food_id': str(food.id),
        'selected_food_cal': '95',
        'submit_choose': 'Add Selected Food'
    }, follow_redirects=True)
    assert b'Logged "Apple"' in rv.data
    logs = MealLog.query.all()
    assert len(logs) == 1
    assert logs[0].food.calories == 95

# 5: Missing selection errors
def test_search_without_selection(auth_user, client):
    dt = datetime.now().strftime('%Y-%m-%dT%H:%M')
    rv = client.post('/dashboard', data={
        'meal_date_time': dt,
        'search_food': 'Banana',
        'submit_choose': 'Add Selected Food'
    }, follow_redirects=True)
    assert b'Please pick a food' in rv.data
    assert MealLog.query.count() == 0

# 6: Invalid custom meal missing fields
@pytest.mark.parametrize("name,calories", [('', '100'), ('Name', ''), ('', '')])
def test_invalid_custom_missing(auth_user, client, name, calories):
    dt = datetime.now().strftime('%Y-%m-%dT%H:%M')
    rv = client.post('/dashboard', data={
        'meal_date_time': dt,
        'custom_name': name,
        'custom_calories': calories,
        'submit_custom': 'Add Custom Food'
    }, follow_redirects=True)
    assert b'Provide both a name' in rv.data
    assert MealLog.query.count() == 0

# 7: Invalid datetime format
def test_invalid_datetime_format(auth_user, client):
    rv = client.post('/dashboard', data={
        'meal_date_time': 'bad-format',
        'custom_name': 'Test',
        'custom_calories': '50',
        'submit_custom': 'Add Custom Food'
    }, follow_redirects=True)
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
    # create two logs on today
    f1 = Food(name='X', calories=10, serving_size='')
    f2 = Food(name='Y', calories=20, serving_size='')
    db.session.add_all([f1, f2]); db.session.flush()
    db.session.add_all([
        MealLog(user_id=user.id, food_id=f1.id, date=today),
        MealLog(user_id=user.id, food_id=f2.id, date=today)
    ])
    db.session.commit()
    rv = client.get('/api/calorie-data')
    data = rv.get_json()
    # find today's label
    today_label = today.strftime('%a')
    # should have sum 30 for today index
    result = next(item for item in data if item['label']==today_label)
    assert result['calories'] == 30

# 10: Food search endpoint
def test_api_food_search(client, auth_user):
    # seed local DB
    f = Food(name='Pear', calories=50, serving_size='')
    db.session.add(f); db.session.commit()
    rv = client.get('/api/foods?q=Pe')
    results = rv.get_json()
    assert any(r['name']=='Pear' for r in results)


# --------------------
# Selenium tests
# --------------------

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytest
import time

@pytest.fixture(scope='module')
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    d = webdriver.Chrome(options=options)
    yield d
    d.quit()

# 1: Login flow
@pytest.mark.selenium
def test_login_flow(driver):
    driver.get('http://127.0.0.1:5000/login')
    driver.find_element(By.NAME, 'username').send_keys('tester')
    driver.find_element(By.NAME, 'password').send_keys('secret')
    driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
    WebDriverWait(driver,5).until(EC.url_contains('/dashboard'))
    assert 'dashboard' in driver.current_url

# 2: Open modal
@pytest.mark.selenium
def test_open_modal(driver):
    driver.get('http://127.0.0.1:5000/dashboard')
    btn = WebDriverWait(driver,5).until(EC.element_to_be_clickable((By.ID,'openMealModalBtn')))
    btn.click()
    assert driver.find_element(By.ID,'mealModal').is_displayed()

# 3: Custom tab defaults disabled
@pytest.mark.selenium
def test_custom_tab_disables_search(driver):
    driver.get('http://127.0.0.1:5000/dashboard')
    driver.find_element(By.ID,'openMealModalBtn').click()
    driver.find_element(By.ID,'inputOwnTabBtn').click()
    assert driver.find_element(By.NAME,'custom_name').is_enabled()
    driver.find_element(By.ID,'chooseFoodTabBtn').click()
    assert not driver.find_element(By.NAME,'custom_name').is_enabled()

# 4: Add custom meal
@pytest.mark.selenium
def test_add_custom_via_selenium(driver):
    driver.get('http://127.0.0.1:5000/dashboard')
    time.sleep(1)
    driver.find_element(By.ID,'openMealModalBtn').click()
    driver.find_element(By.ID,'inputOwnTabBtn').click()
    # set date via JS
    dt = datetime.now().strftime('%Y-%m-%dT%H:%M')
    dp = driver.find_element(By.CSS_SELECTOR,'.date-picker')
    driver.execute_script("arguments[0].value=arguments[1]", dp, dt)
    driver.find_element(By.NAME,'custom_name').send_keys('Sushi')
    driver.find_element(By.NAME,'custom_calories').send_keys('250')
    driver.find_element(By.ID,'submitCustomBtn').click()
    WebDriverWait(driver,5).until(EC.text_to_be_present_in_element((By.TAG_NAME,'tbody'),'Sushi'))
    assert '250' in driver.page_source

# 5: Search and select meal
@pytest.mark.selenium
def test_search_and_select(driver):
    driver.get('http://127.0.0.1:5000/dashboard')
    driver.find_element(By.ID,'openMealModalBtn').click()
    # search exists
    driver.find_element(By.ID,'searchFoodInput').send_keys('Sushi')
    driver.find_element(By.ID,'searchFoodBtn').click()
    WebDriverWait(driver,5).until(EC.presence_of_element_located((By.CSS_SELECTOR,'.food-item')))
    item = driver.find_element(By.CSS_SELECTOR,'.food-item')
    item.click()
    assert driver.find_element(By.ID,'submitChooseBtn').is_enabled()

# 6: Submit choose meal
@pytest.mark.selenium
def test_add_search_via_selenium(driver):
    driver.get('http://127.0.0.1:5000/dashboard')
    driver.find_element(By.ID,'openMealModalBtn').click()
    driver.find_element(By.ID,'searchFoodInput').send_keys('Sushi')
    driver.find_element(By.ID,'searchFoodBtn').click()
    WebDriverWait(driver,5).until(EC.presence_of_element_located((By.CSS_SELECTOR,'.food-item')))
    driver.find_element(By.CSS_SELECTOR,'.food-item').click()
    driver.find_element(By.ID,'submitChooseBtn').click()
    WebDriverWait(driver,5).until(EC.text_to_be_present_in_element((By.TAG_NAME,'tbody'),'Sushi'))
    assert '250' in driver.page_source

# 7: Disabled submit without selection
@pytest.mark.selenium
def test_choose_button_disabled_initially(driver):
    driver.get('http://127.0.0.1:5000/dashboard')
    driver.find_element(By.ID,'openMealModalBtn').click()
    assert not driver.find_element(By.ID,'submitChooseBtn').is_enabled()

# 8: Week navigation prev/next buttons
@pytest.mark.selenium
def test_week_nav(driver):
    driver.get('http://127.0.0.1:5000/calorie-counter')
    prev = driver.find_element(By.CSS_SELECTOR,'form[action*="calorie_counter"] .week-btn')
    assert prev.is_displayed()

# 9: Refresh scoreboard button works
@pytest.mark.selenium
def test_refresh_scoreboard(driver):
    driver.get('http://127.0.0.1:5000/dashboard')
    btn = driver.find_element(By.CSS_SELECTOR,'button[onclick="refreshScoreboard()"]')
    btn.click()
    # Assuming partial scoreboard updates without errors
    assert 'scoreboard' in driver.page_source

# 10: Leaderboard link navigates
@pytest.mark.selenium
def test_leaderboard_link(driver):
    driver.get('http://127.0.0.1:5000/dashboard')
    driver.find_element(By.LINK_TEXT,'View More').click()
    WebDriverWait(driver,5).until(EC.url_contains('/leaderboard'))
    assert '/leaderboard' in driver.current_url
