# app/usda.py

import requests
from flask import current_app, session, has_request_context
from app.models import User
from app import db

BASE_URL = "https://api.nal.usda.gov/fdc/v1"
DEMO_KEY = "DEMO_KEY"  

def _get_key():
    if has_request_context():
        user_id = session.get('user_id')
        if user_id:
            user = db.session.get(User, user_id)
            if user and user.usda_api_key:
                return user.usda_api_key

        app_key = current_app.config.get('FDC_API_KEY')
        if app_key:
            return app_key

    # Fallback when outside request or no key
    return DEMO_KEY

def search_foods(query, page_size=5, data_types=None):
    api_key = _get_key()
    if not api_key:
        print("[DEBUG] No API key found!")
        return []

    # USDA expects the key as a query param, not in the JSON body
    query_params = {"api_key": api_key}
    body = {
        "query": query,
        "pageSize": page_size
    }
    if data_types:
        body["dataType"] = data_types

    try:
        resp = requests.post(
            f"{BASE_URL}/foods/search",
            params=query_params,
            json=body,
            timeout=5
        )
        resp.raise_for_status()
        return resp.json().get("foods", [])
    except requests.exceptions.RequestException as e:
        print(f"[FDC API Error] {e}")
        return []

def get_food_details(fdc_id):
    api_key = _get_key()
    try:
        resp = requests.get(
            f"{BASE_URL}/food/{fdc_id}",
            params={"api_key": api_key},
            timeout=5
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        print(f"[FDC API Error] {e}")
        return None

def get_food_calories(fdc_id):
    """
    Fetch just the calorie value from the food details, or None if not found.
    """
    data = get_food_details(fdc_id)
    if not data:
        return None

    for nutrient in data.get("foodNutrients", []):
        if nutrient.get("nutrientName") == "Energy":
            return nutrient.get("value")
    return None