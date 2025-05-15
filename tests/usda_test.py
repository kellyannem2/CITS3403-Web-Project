import pytest
from unittest.mock import patch, MagicMock
from flask import current_app
from app import db, app
from app.models import User
from app.usda import search_foods, get_food_details

@pytest.fixture
def user_and_login(client):
    user = User(username="foodie", full_name="USDA Fan", email="foodie@x.com", password="x", is_verified=True)
    db.session.add(user)
    db.session.commit()
    with client.session_transaction() as sess:
        sess["user_id"] = user.id
    return user

def test_search_foods_no_key(client, user_and_login):
    with app.test_request_context():
        current_app.config["FDC_API_KEY"] = None
        res = search_foods("banana")
    assert res == []

@patch("app.usda.requests.post")
def test_search_foods_success(mock_post, client, user_and_login):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"foods": [{"description": "banana", "fdcId": 123}]}
    mock_post.return_value = mock_resp

    with app.test_request_context():
        current_app.config["FDC_API_KEY"] = "mockkey"
        results = search_foods("banana")
    assert results[0]["description"] == "banana"

@patch("app.usda.requests.get")
def test_get_food_details_success(mock_get, client, user_and_login):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"fdcId": 123, "description": "banana"}
    mock_get.return_value = mock_resp

    with app.test_request_context():
        current_app.config["FDC_API_KEY"] = "mockkey"
        result = get_food_details(123)
    assert result["fdcId"] == 123

def test_get_food_details_no_key(client, user_and_login):
    with app.test_request_context():
        current_app.config["FDC_API_KEY"] = None
        with pytest.raises(RuntimeError, match="No USDA API key available"):
            get_food_details(123)
