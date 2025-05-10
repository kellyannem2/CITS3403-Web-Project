# app/usda.py

import requests
from flask import current_app, session
from app.models import User
from app import db

BASE_URL = "https://api.nal.usda.gov/fdc/v1"

def _get_key():
    # Try per-user key first
    user_id = session.get('user_id')
    if user_id:
        user = db.session.get(User, user_id)
        if user and user.usda_api_key:
            return user.usda_api_key
    # Fallback to global key
    return current_app.config.get('FDC_API_KEY')

def search_foods(query, page_size=25, data_types=None):
    api_key = _get_key()
    if not api_key:
        # No key available → return empty list so caller can handle
        return []
    params = {
        "api_key": api_key,
        "query": query,
        "pageSize": page_size,
    }
    if data_types:
        params["dataType"] = data_types
    resp = requests.post(f"{BASE_URL}/foods/search", json=params, timeout=5)
    resp.raise_for_status()
    return resp.json().get("foods", [])

def get_food_details(fdc_id):
    api_key = _get_key()
    if not api_key:
        raise RuntimeError("No USDA API key available")
    resp = requests.get(
        f"{BASE_URL}/food/{fdc_id}",
        params={"api_key": api_key},
        timeout=5
    )
    resp.raise_for_status()
    return resp.json()
