import sys, os
# ensure project root is on sys.path so `import app` works
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import threading, time
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

# ────────────────────────────
#  Live Flask server fixture
# ────────────────────────────
@pytest.fixture(scope='module', autouse=True)
def flask_server():
    db_path = os.path.join(os.getcwd(), 'test.db')
    if os.path.exists(db_path): os.remove(db_path)

    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'WTF_CSRF_ENABLED': False,
    })

    ctx = app.app_context()
    ctx.push()
    db.create_all()
    user = User(
        username='tester', full_name='Tester',
        email='tester@example.com',
        password=generate_password_hash('secret'),
        is_verified=True
    )
    sushi = Food(name='Sushi', calories=250, serving_size='1 unit')
    db.session.add_all([user, sushi])
    db.session.commit()

    server = threading.Thread(
        target=app.run,
        kwargs={'host':'127.0.0.1','port':5000,'threaded':True,'use_reloader':False}
    )
    server.daemon = True
    server.start()
    time.sleep(1)
    yield

    db.drop_all()
    ctx.pop()
    if os.path.exists(db_path): os.remove(db_path)

# ────────────────────────────
#  Selenium WebDriver fixture
# ────────────────────────────
@pytest.fixture(scope='module')
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--incognito")
    options.add_argument('--disable-gpu')

    service = Service(ChromeDriverManager().install())
    drv = webdriver.Chrome(service=service, options=options)
    yield drv
    drv.quit()


# ────────────────────────────
#  Selenium tests
# ────────────────────────────

@pytest.mark.selenium
def test_login_flow(driver):
    driver.get('http://127.0.0.1:5000/login')
    driver.find_element(By.NAME,'username').send_keys('tester')
    driver.find_element(By.NAME,'password').send_keys('secret')
    driver.find_element(By.CSS_SELECTOR,"button[type='submit']").click()
    WebDriverWait(driver,5).until(EC.url_contains('/dashboard'))
    assert '/dashboard' in driver.current_url

@pytest.mark.selenium
def test_open_modal(driver):
    driver.get('http://127.0.0.1:5000/dashboard')
    WebDriverWait(driver,5).until(EC.element_to_be_clickable((By.ID,'openMealModalBtn'))).click()
    modal = WebDriverWait(driver,5).until(EC.visibility_of_element_located((By.CSS_SELECTOR,'#mealModal.show')))
    assert modal.is_displayed()

@pytest.mark.selenium
def test_custom_tab_disables_search(driver):
    driver.get('http://127.0.0.1:5000/dashboard')
    WebDriverWait(driver,5).until(EC.element_to_be_clickable((By.ID,'openMealModalBtn'))).click()
    WebDriverWait(driver,5).until(EC.element_to_be_clickable((By.ID,'inputOwnTabBtn'))).click()
    assert driver.find_element(By.NAME,'custom_name').is_enabled()
    driver.find_element(By.ID,'chooseFoodTabBtn').click()
    assert not driver.find_element(By.NAME,'custom_name').is_enabled()

@pytest.mark.selenium
def test_add_custom_via_selenium(driver):
    driver.get('http://127.0.0.1:5000/dashboard')
    WebDriverWait(driver,5).until(EC.element_to_be_clickable((By.ID,'openMealModalBtn'))).click()
    WebDriverWait(driver,5).until(EC.element_to_be_clickable((By.ID,'inputOwnTabBtn'))).click()
    dt = datetime.now().strftime('%Y-%m-%dT%H:%M')
    dp = driver.find_element(By.CSS_SELECTOR,'.date-picker')
    driver.execute_script("arguments[0].value=arguments[1]", dp, dt)
    driver.find_element(By.NAME,'custom_name').send_keys('UniqueSushi')
    driver.find_element(By.NAME,'custom_calories').send_keys('250')
    driver.find_element(By.ID,'submitCustomBtn').click()
    WebDriverWait(driver,5).until(EC.text_to_be_present_in_element((By.CSS_SELECTOR,'.columns .column:nth-child(3) table tbody'),'UniqueSushi'))


"""@pytest.mark.selenium
def test_search_and_select(driver):
    driver.get('http://127.0.0.1:5000/dashboard')
    WebDriverWait(driver,10).until(
        EC.element_to_be_clickable((By.ID,'openMealModalBtn'))
    ).click()
    WebDriverWait(driver,10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR,'#mealModal.show'))
    )
    search = WebDriverWait(driver,10).until(
        EC.element_to_be_clickable((By.ID,'searchFoodInput'))
    )
    search.clear(); search.send_keys('Sushi')
    WebDriverWait(driver,10).until(
        EC.element_to_be_clickable((By.ID,'searchFoodBtn'))
    ).click()
    item = WebDriverWait(driver,10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR,'.food-item'))
    )
    assert item.is_displayed()
    item.click()
    submit = WebDriverWait(driver,10).until(
        EC.element_to_be_clickable((By.ID,'submitChooseBtn'))
    )
    assert submit.is_enabled()"""

"""@pytest.mark.selenium
def test_add_search_via_selenium(driver):
    driver.get('http://127.0.0.1:5000/dashboard')
    WebDriverWait(driver,10).until(
        EC.element_to_be_clickable((By.ID,'openMealModalBtn'))
    ).click()
    WebDriverWait(driver,10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR,'#mealModal.show'))
    )
    search = WebDriverWait(driver,10).until(
        EC.element_to_be_clickable((By.ID,'searchFoodInput'))
    )
    search.clear(); search.send_keys('Sushi')
    WebDriverWait(driver,10).until(
        EC.element_to_be_clickable((By.ID,'searchFoodBtn'))
    ).click()
    item = WebDriverWait(driver,10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR,'.food-item'))
    )
    item.click()
    WebDriverWait(driver,10).until(
        EC.element_to_be_clickable((By.ID,'submitChooseBtn'))
    ).click()
    # wait for modal disappearance
    WebDriverWait(driver,10).until(
        EC.invisibility_of_element_located((By.CSS_SELECTOR,'#mealModal.show'))
    )
    tbody_sel = '.dashboard-columns .column:nth-child(3) table tbody'
    WebDriverWait(driver,10).until(
        EC.text_to_be_present_in_element((By.CSS_SELECTOR,tbody_sel),'Sushi')
    )
    assert 'Sushi' in driver.find_element(By.CSS_SELECTOR,tbody_sel).text"""

@pytest.mark.selenium
def test_choose_button_disabled_initially(driver):
    driver.get('http://127.0.0.1:5000/dashboard')
    WebDriverWait(driver,5).until(EC.element_to_be_clickable((By.ID,'openMealModalBtn'))).click()
    assert not driver.find_element(By.ID,'submitChooseBtn').is_enabled()

@pytest.mark.selenium
def test_week_nav(driver):
    driver.get('http://127.0.0.1:5000/calorie-counter')
    prev = driver.find_element(By.CSS_SELECTOR,"form[action*='/calorie-counter'] .week-btn")
    assert prev.is_displayed()

@pytest.mark.selenium
def test_refresh_scoreboard(driver):
    driver.get('http://127.0.0.1:5000/dashboard')
    driver.find_element(By.CSS_SELECTOR,"button[onclick='refreshScoreboard()']").click()
    assert 'scoreboard' in driver.page_source

"""@pytest.mark.selenium
def test_leaderboard_link(driver):
    driver.get('http://127.0.0.1:5000/dashboard')
    btn = WebDriverWait(driver,10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR,'.dashboard-columns .column:nth-child(1) .btn-link'))
    )
    btn.click()
    WebDriverWait(driver,10).until(
        EC.url_contains('/leaderboard')
    )
    assert '/leaderboard' in driver.current_url"""
