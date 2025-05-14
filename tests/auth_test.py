import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import app, db
from app.models import User
from werkzeug.security import generate_password_hash

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()

def test_login_invalid_user(client):
    response = client.post("/login", data={"username": "ghost", "password": "wrong"}, follow_redirects=True)
    assert b"New User" in response.data

def test_login_invalid_password(client):
    user = User(username="bob", full_name="Bob Test", email="bob@example.com", password=generate_password_hash("secret"), is_verified=True)
    db.session.add(user)
    db.session.commit()

    response = client.post("/login", data={"username": "bob", "password": "wrong"}, follow_redirects=True)
    assert b"Invalid credentials" in response.data

def test_login_unverified_user(client):
    user = User(username="jane", full_name="Jane Unverified", email="jane@example.com", password=generate_password_hash("pass"), is_verified=False)
    db.session.add(user)
    db.session.commit()

    response = client.post("/login", data={"username": "jane", "password": "pass"}, follow_redirects=True)
    assert b"User not verified" in response.data

def test_signup_password_mismatch(client):
    response = client.post("/signup", data={
        "username": "newbie",
        "email": "newbie@example.com",
        "password": "one",
        "confirm_password": "two",
        "firstNameInput": "New",
        "lastNameInput": "User"
    }, follow_redirects=True)
    assert b"Passwords do not match" in response.data

def test_signup_duplicate_username(client):
    user = User(username="taken", full_name="Test", email="test@example.com", password="x")
    db.session.add(user)
    db.session.commit()

    response = client.post("/signup", data={
        "username": "taken",
        "email": "another@example.com",
        "password": "abc",
        "confirm_password": "abc",
        "firstNameInput": "New",
        "lastNameInput": "Person"
    }, follow_redirects=True)
    assert b"Username already exists" in response.data

def test_verify_email_token_invalid(client):
    response = client.get("/verify_email/invalidtoken", follow_redirects=True)
    assert b"Invalid or expired link" in response.data

def test_logout(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 1
    response = client.get("/logout", follow_redirects=True)
    assert b"You have been logged out" in response.data

from unittest.mock import patch
from io import BytesIO

# --- SETTINGS: password update ---
def test_change_password_success(client):
    hashed = generate_password_hash("oldpw")
    user = User(username="pchange", full_name="Test", email="a@b.com", password=hashed, is_verified=True)
    db.session.add(user)
    db.session.commit()

    with client.session_transaction() as sess:
        sess["user_id"] = user.id

    response = client.post("/settings", data={
        "action": "change_password",
        "current_password": "oldpw",
        "password": "newpw",
        "confirm_password": "newpw"
    }, follow_redirects=True)
    assert b"Password updated successfully" in response.data

def test_change_password_wrong_current(client):
    user = User(username="wrongpw", full_name="Test", email="a@b.com", password=generate_password_hash("right"), is_verified=True)
    db.session.add(user)
    db.session.commit()

    with client.session_transaction() as sess:
        sess["user_id"] = user.id

    res = client.post("/settings", data={
        "action": "change_password",
        "current_password": "wrong",
        "password": "newpw",
        "confirm_password": "newpw"
    }, follow_redirects=True)
    assert b"Current password is incorrect" in res.data

# --- SHARE SNAPSHOT ---
def test_share_snapshot_user_not_found(client):
    response = client.post("/share_snapshot", data={"recipient_username": "someone"}, follow_redirects=True)
    assert b"You must be logged in to share" in response.data

def test_share_snapshot_invalid_username(client):
    user = User(username="sender", full_name="Sender", email="a@a.com", password="pw", is_verified=True)
    db.session.add(user)
    db.session.commit()

    with client.session_transaction() as sess:
        sess["user_id"] = user.id

    response = client.post("/share_snapshot", data={"recipient_username": "noone"}, follow_redirects=True)
    assert b"User not found" in response.data

# --- UPLOAD AVATAR ---
def test_upload_avatar_no_file(client):
    user = User(username="avatarless", full_name="NoPic", email="a@b.com", password="x", is_verified=True)
    db.session.add(user)
    db.session.commit()
    with client.session_transaction() as sess:
        sess["user_id"] = user.id

    res = client.post("/upload_avatar", data={}, follow_redirects=True)
    assert b"No file selected" in res.data

def test_upload_avatar_invalid_filetype(client):
    user = User(username="badpic", full_name="BadPic", email="a@b.com", password="x", is_verified=True)
    db.session.add(user)
    db.session.commit()
    with client.session_transaction() as sess:
        sess["user_id"] = user.id

    fake_file = (BytesIO(b"fake"), "avatar.exe")
    data = {"avatar": fake_file}

    res = client.post("/upload_avatar", data=data, content_type="multipart/form-data", follow_redirects=True)
    assert b"Please upload an image file" in res.data

# --- VERIFY EMAIL CHANGE (invalid token) ---
def test_verify_email_change_invalid(client):
    res = client.get("/verify_email_change/faketoken", follow_redirects=True)
    assert b"Invalid or expired email change link" in res.data
