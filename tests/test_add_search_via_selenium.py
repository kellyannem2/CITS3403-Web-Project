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
def test_add_search_via_selenium(driver):
    # 1. Login and navigate
    do_login(driver)

    # 2. Open the meal modal
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'openMealModalBtn'))
    ).click()

    # 3. Wait for the search input to appear (modal is open)
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, 'searchFoodInput'))
    )

    # 4. Perform the search
    search_input = driver.find_element(By.ID, 'searchFoodInput')
    search_input.clear()
    search_input.send_keys('Sushi')
    driver.find_element(By.ID, 'searchFoodBtn').click()

    # 5. Wait for at least one result and click the first
    items = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.food-item'))
    )
    items[0].click()

    # 5.1 Wait for selection to register
    WebDriverWait(driver, 5).until(
        lambda d: "selected" in items[0].get_attribute("class")
    )

    # 5.2 Wait until button is enabled
    submit_btn = WebDriverWait(driver, 5).until(
        lambda d: driver.find_element(By.ID, 'submitChooseBtn').is_enabled()
    )

    # 6. Click the now-enabled button
    submit_btn = driver.find_element(By.ID, 'submitChooseBtn')
    if submit_btn.is_enabled():
        submit_btn.click()

    # 7. Finally, verify the new row appears in column 3’s table
    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, '.columns .column:nth-child(3) table tbody'),
            'Sushi'
        )
    )
    tbody = driver.find_element(
        By.CSS_SELECTOR, '.columns .column:nth-child(3) table tbody'
    )
    assert 'Sushi' in tbody.text and '250' in tbody.text