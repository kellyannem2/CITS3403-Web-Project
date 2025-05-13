from flask import request, jsonify
from app.models import User
from app import app


@app.route('/search_usernames')
def search_usernames():
    query = request.args.get('q', '').lower()
    matches = User.query.filter(User.username.ilike(f'%{query}%')).limit(5).all()
    return jsonify([user.username for user in matches])
