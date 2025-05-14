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
from selenium.webdriver.common.keys import Keys
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
    opts = webdriver.ChromeOptions()
    opts.add_argument('--headless'); opts.add_argument('--no-sandbox')
    service = Service(ChromeDriverManager().install())
    drv = webdriver.Chrome(service=service, options=opts)
    yield drv; drv.quit()

# ────────────────────────────────
# Utility: log in as tester
# ────────────────────────────────
def do_login(driver):
    driver.get('http://127.0.0.1:5000/login')
    # fill credentials
    WebDriverWait(driver,10).until(
        EC.presence_of_element_located((By.NAME,'username'))
    ).send_keys('tester')
    driver.find_element(By.NAME,'password').send_keys('secret')
    # click the submit button
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    # wait for dashboard load
    WebDriverWait(driver,10).until(
        EC.presence_of_element_located((By.ID,'openMealModalBtn'))
    )

# ────────────────────────────────
# Selenium tests
# ────────────────────────────────

@pytest.mark.selenium
def test_leaderboard_link(driver):
    do_login(driver)
    # click the leaderboard "View More"
    link = WebDriverWait(driver,10).until(
        EC.element_to_be_clickable((By.LINK_TEXT,'View More'))
    )
    link.click()
    WebDriverWait(driver,10).until(
        EC.url_contains('/leaderboard')
    )
    assert '/leaderboard' in driver.current_url
