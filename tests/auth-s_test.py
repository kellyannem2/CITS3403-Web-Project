import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import threading, time, pytest
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
# Flask test server fixture
# ────────────────────────────────
@pytest.fixture(scope='module', autouse=True)
def flask_server():
    db_file = 'test_ui.db'
    if os.path.exists(db_file):
        os.remove(db_file)

    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{os.path.abspath(db_file)}',
        'WTF_CSRF_ENABLED': False
    })

    ctx = app.app_context(); ctx.push()
    db.create_all()

    # Seed user and food
    user = User(
        username='tester',
        full_name='Tester',
        email='test@example.com',
        password=generate_password_hash('secret'),
        is_verified=True
    )
    food = Food(name='Sushi', calories=250, serving_size='1 unit')
    db.session.add_all([user, food]); db.session.commit()

    server = threading.Thread(
        target=app.run,
        kwargs={'host': '127.0.0.1', 'port': 5000, 'use_reloader': False}
    )
    server.daemon = True; server.start()
    time.sleep(2)
    yield
    db.drop_all(); ctx.pop()
    if os.path.exists(db_file):
        os.remove(db_file)

# ────────────────────────────────
# Selenium WebDriver fixture
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
# Utility: log in as test user
# ────────────────────────────────
def do_login(driver):
    driver.get('http://127.0.0.1:5000/login')
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, 'username'))
    ).send_keys('tester')
    driver.find_element(By.NAME, 'password').send_keys('secret')
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'openMealModalBtn'))
    )

# ────────────────────────────────
# Selenium UI Tests
# ────────────────────────────────

@pytest.mark.selenium
def test_account_page_loads(driver):
    do_login(driver)
    driver.get("http://127.0.0.1:5000/account")

    # 1) Heading should read "My Account"
    heading = WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "account-heading"))
    )
    assert heading.text.strip() == "My Account"

    # 2) Email-change form and its button exist
    email_input = driver.find_element(By.ID, "new_email")
    submit_btn  = driver.find_element(By.ID, "emailSubmitBtn")
    assert email_input.is_displayed()
    assert submit_btn.is_displayed()

@pytest.mark.selenium
def test_invalid_password_change(driver):
    do_login(driver)
    driver.get("http://127.0.0.1:5000/account")

    # Click the "Change Password" tab
    pwd_tab = driver.find_element(By.CSS_SELECTOR, ".tab-link[data-tab='tab-password']")
    pwd_tab.click()

    # Wait for the current-password field
    WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.ID, "current_password"))
    )

    # Submit wrong current password
    driver.find_element(By.ID, "current_password").send_keys("wrongpass")
    driver.find_element(By.ID, "new_password").send_keys("newpass123")
    driver.find_element(By.ID, "confirm_new_password").send_keys("newpass123")
    driver.find_element(By.ID, "passwordSubmitBtn").click()

    # Expect an "incorrect" error message somewhere on page
    WebDriverWait(driver, 5).until(
        lambda d: "incorrect" in d.page_source.lower()
    )

@pytest.mark.selenium
def test_invalid_avatar_upload(driver):
    do_login(driver)
    driver.get("http://127.0.0.1:5000/account")

    # Create a dummy non-image file
    test_file = "not_an_image.txt"
    with open(test_file, "w") as f:
        f.write("this is not an image")

    # Upload via the hidden input
    avatar_input = driver.find_element(By.ID, "avatar-input")
    avatar_input.send_keys(os.path.abspath(test_file))
    # form auto-submits on change
    WebDriverWait(driver, 5).until(
        lambda d: "image file" in d.page_source.lower()
    )
    os.remove(test_file)

@pytest.mark.selenium
def test_logout_flow(driver):
    do_login(driver)
    driver.get("http://127.0.0.1:5000/account")

    # Click the logout button (which triggers a JS confirm())
    logout_btn = driver.find_element(By.CSS_SELECTOR, ".logout-form button[type='submit']")
    logout_btn.click()

    # Handle the JS confirm popup
    WebDriverWait(driver, 5).until(EC.alert_is_present())
    alert = driver.switch_to.alert
    assert "are you sure" in alert.text.lower()
    alert.accept()

    # Now check that logout was successful
    WebDriverWait(driver, 5).until(
        lambda d: "you have been logged out" in d.page_source.lower()
        or d.current_url.endswith("/login")
    )