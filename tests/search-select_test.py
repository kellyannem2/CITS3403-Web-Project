import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import threading, time
import pytest
from datetime import datetime
from werkzeug.security import generate_password_hash

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app import app, db
from app.models import User, Food

# ────────────────────────────────
# Flask server fixture
# ────────────────────────────────
@pytest.fixture(scope='module', autouse=True)
def flask_server():
    db_file = 'test_ui.db'
    if os.path.exists(db_file): os.remove(db_file)

    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{os.path.abspath(db_file)}',
        'WTF_CSRF_ENABLED': False
    })
    ctx = app.app_context(); ctx.push()
    db.create_all()
    # seed a user and a food record
    user = User(username='tester', full_name='Tester', email='test@example.com',
                password=generate_password_hash('secret'), is_verified=True)
    food = Food(name='Sushi', calories=250, serving_size='1 unit')
    db.session.add_all([user, food]); db.session.commit()

    server = threading.Thread(
        target=app.run,
        kwargs={'host':'127.0.0.1','port':5000,'use_reloader':False}
    )
    server.daemon = True; server.start()
    time.sleep(1)
    yield
    db.drop_all(); ctx.pop()
    if os.path.exists(db_file): os.remove(db_file)

# ────────────────────────────────
# WebDriver fixture
# ────────────────────────────────
@pytest.fixture(scope='module')
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--incognito")


    service = Service(ChromeDriverManager().install())
    drv = webdriver.Chrome(service=service, options=options)
    yield drv
    drv.quit()

# ────────────────────────────────
# Utility: log in as tester
# ────────────────────────────────
def do_login(driver):
    driver.get('http://127.0.0.1:5000/login')
    WebDriverWait(driver,10).until(
        EC.presence_of_element_located((By.NAME,'username'))
    ).send_keys('tester')
    driver.find_element(By.NAME,'password').send_keys('secret')
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    WebDriverWait(driver,10).until(
        EC.presence_of_element_located((By.ID,'openMealModalBtn'))
    )

# ────────────────────────────────
# Selenium tests
# ────────────────────────────────

@pytest.mark.selenium
def test_search_and_select(driver):
    do_login(driver)
    driver.find_element(By.ID,'openMealModalBtn').click()
    WebDriverWait(driver,10).until(lambda d: 'show' in d.find_element(By.ID,'mealModal').get_attribute('class'))
    search_input = driver.find_element(By.ID,'searchFoodInput')
    search_input.clear(); search_input.send_keys('Sushi')
    driver.find_element(By.ID,'searchFoodBtn').click()
    items = WebDriverWait(driver,10).until(lambda d: d.find_elements(By.CSS_SELECTOR,'.food-item'))
    assert items, 'No food-item elements found'
    items[0].click()
    WebDriverWait(driver,10).until(lambda d: d.find_element(By.ID,'submitChooseBtn').is_enabled())
    assert driver.find_element(By.ID,'submitChooseBtn').is_enabled()