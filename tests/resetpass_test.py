import pytest
from app import db
from app.models import User
from werkzeug.security import check_password_hash

@pytest.fixture
def user_and_login(client):
    user = User(username="resetuser", full_name="Reset User", email="reset@x.com", password="x", is_verified=True)
    db.session.add(user)
    db.session.commit()
    return user

def test_reset_pass_invalid_email(client):
    res = client.post("/reset_pass", data={"email": "notfound@example.com"}, follow_redirects=True)
    assert b"Email not found" in res.data

def test_reset_pass_valid_email(client, user_and_login):
    res = client.post("/reset_pass", data={"email": user_and_login.email}, follow_redirects=True)
    assert b"Password reset link sent" in res.data

def test_reset_pass_mail_failure(client, user_and_login, monkeypatch):
    def fake_send(*args, **kwargs):
        raise Exception("mail fail")
    monkeypatch.setattr("flask_mail.Mail.send", fake_send)

    res = client.post("/reset_pass", data={"email": user_and_login.email}, follow_redirects=True)
    assert b"Password reset link sent" in res.data  # Still shows success

def test_reset_password_invalid_token(client):
    res = client.get("/reset_password/invalidtoken", follow_redirects=True)
    assert b"Invalid or expired token" in res.data

def test_reset_password_valid_token(client, user_and_login):
    user_and_login.reset_token = "validtoken123"
    db.session.commit()

    res_get = client.get("/reset_password/validtoken123")
    assert b"reset_pass.html" in res_get.data or res_get.status_code == 200

    res_post = client.post("/reset_password/validtoken123", data={"password": "newpass123"}, follow_redirects=True)
    assert b"Password reset successfully" in res_post.data

    updated = db.session.get(User, user_and_login.id)
    assert check_password_hash(updated.password, "newpass123")
    assert updated.reset_token is None
