from flask import render_template, session, redirect, url_for, flash, request, jsonify, current_app
from app import app, db
from sqlalchemy import func
from app.models import User, Scoreboard, ExerciseLog, MealLog, Food
from datetime import date, timedelta
from .forms import MealForm
from app.usda import search_foods
from datetime import datetime

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    form = MealForm()

    if request.method == "POST":
        # 1) Always grab the one datetime
        dt_str = request.form.get("meal_date_time")
        try:
            # parse the ISO string (flatpickr now emits “YYYY-MM-DDTHH:MM”)
            meal_dt = datetime.fromisoformat(dt_str)
        except Exception:
            flash("Invalid date/time format.", "error")
            return redirect(url_for("dashboard"))

        # 2) Branch on which button was clicked
        if "submit_choose" in request.form:
            # Search tab
            food_id = request.form.get("selected_food_id")
            if not food_id:
                flash("Please pick a food from the search results.", "warning")
                return redirect(url_for("dashboard"))

            food = Food.query.get(food_id)
            if not food:
                flash("That food isn’t in our database any more—please search again.", "error")
                return redirect(url_for("dashboard"))

        elif "submit_custom" in request.form:
            # Custom tab
            name = request.form.get("custom_name","").strip()
            cal  = request.form.get("custom_calories","").strip()
            if not name or not cal.isdigit():
                flash("Provide both a name (text) and calories (number).", "warning")
                return redirect(url_for("dashboard"))

            food = Food(name=name, calories=int(cal), serving_size="(custom)")
            db.session.add(food)
            db.session.flush()

        else:
            flash("Unknown action.", "error")
            return redirect(url_for("dashboard"))

        # 3) Log it
        new_log = MealLog(user_id=session["user_id"], food_id=food.id, date=meal_dt)
        db.session.add(new_log)
        db.session.commit()

        flash(f"Logged “{food.name}” – {food.calories} cal @ {meal_dt}", "success")
        return redirect(url_for("dashboard"))

    # 2) GET or invalid POST: render dashboard
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    user = User.query.get(user_id)
    if not user:
        session.pop("user_id", None)
        flash("User not found, please log in again.", "error")
        return redirect(url_for("login"))

    # 🔹 Total calories burned today
    total_calories = db.session.query(
        func.sum(ExerciseLog.calories_burned)
    ).filter(
        ExerciseLog.user_id == user.id,
        ExerciseLog.date == date.today()
    ).scalar() or 0

    # 🔹 Today's exercises
    todays_exercises = ExerciseLog.query.filter_by(
        user_id=user.id,
        date=date.today()
    ).all()

    # 🔹 Scoreboard update or creation
    scoreboard_entry = Scoreboard.query.filter_by(
        user_id=user.id,
        timestamp=date.today()
    ).first()

    if scoreboard_entry:
        scoreboard_entry.total_calories_burned = total_calories
    else:
        db.session.add(Scoreboard(
            user_id=user.id,
            total_calories_burned=total_calories,
            timestamp=date.today()
        ))

    db.session.commit()

    # 🔹 Get all teams
    all_teams = db.session.query(User.team).filter(User.team.isnot(None)).distinct().all()
    all_teams = [team[0] for team in all_teams]

    # 🔹 Custom Team Leaderboard: Net Calories = Eaten - Burned
    total_eaten = 0
    team_member_scoreboard = []
    if user.team:
        team_users = User.query.filter_by(team=user.team).all()

        for teammate in team_users:
            today_logs = [log for log in teammate.exercise_logs if log.date == date.today()]
            today_meals = [log for log in teammate.meal_logs if log.date == date.today()]

            if not today_logs or not today_meals:
                continue

            total_burned = sum(log.calories_burned for log in today_logs)
            total_eaten = sum(log.food.calories for log in today_meals)
            net = total_eaten - total_burned

            team_member_scoreboard.append({
                "user": teammate,
                "burned": total_burned,
                "eaten": total_eaten,
                "net": net
            })

        team_member_scoreboard.sort(key=lambda x: x["net"])

    # 🔹 Weekly calories burned chart
    today = date.today()
    week_start = today - timedelta(days=today.weekday())  # Monday

    weekly_results = db.session.query(
        Scoreboard.timestamp,
        func.sum(Scoreboard.total_calories_burned)
    ).filter(
        Scoreboard.user_id == user.id,
        Scoreboard.timestamp >= week_start,
        Scoreboard.timestamp <= today
    ).group_by(Scoreboard.timestamp).all()

    week_data = {record[0].strftime('%a'): float(record[1]) for record in weekly_results}
    labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    chart_data = [week_data.get(day, 0) for day in labels]
    
    return render_template("index.html",
        user=user,
        form=form,
        exercise=user.exercises,
        exercise_log=todays_exercises,
        meal_log=user.meal_logs,
        total_eaten=total_eaten,
        scoreboard=team_member_scoreboard,
        user_total_calories_burnt=total_calories,
        chart_data=chart_data,
        all_teams=all_teams,
        date=date
    )

@app.route("/calorie-counter", methods=["GET", "POST"])
def calorie_counter():
    # Must be logged in
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in to view your meals.", "error")
        return redirect(url_for("login"))

    # Handle form POST
    if request.method == "POST":
        # 1) Parse datetime
        raw_dt = request.form.get("meal_date_time", "")
        try:
            meal_dt = datetime.fromisoformat(raw_dt)
        except Exception:
            flash("Invalid date/time format.", "error")
            return redirect(url_for("calorie_counter"))

        # 2) Branch on which button
        if "submit_choose" in request.form:
            food_id = request.form.get("selected_food_id")
            if not food_id:
                flash("Please pick a food from the search results.", "warning")
                return redirect(url_for("calorie_counter"))
            food = Food.query.get(food_id)
            if not food:
                flash("That food isn’t in our database—please search again.", "error")
                return redirect(url_for("calorie_counter"))

        elif "submit_custom" in request.form:
            name = request.form.get("custom_name", "").strip()
            cal  = request.form.get("custom_calories", "").strip()
            if not name or not cal.isdigit():
                flash("Provide both a name and calories.", "warning")
                return redirect(url_for("calorie_counter"))
            food = Food(name=name, calories=int(cal), serving_size="(custom)")
            db.session.add(food)
            db.session.flush()

        else:
            flash("Unknown action.", "error")
            return redirect(url_for("calorie_counter"))

        # 3) Log it
        new_log = MealLog(user_id=user_id, food_id=food.id, date=meal_dt)
        db.session.add(new_log)
        db.session.commit()
        flash(f"Logged “{food.name}” — {food.calories} cal @ {meal_dt}", "success")
        return redirect(url_for("calorie_counter"))

    # GET: show the page
    # (copy your existing week-nav & query logic here)
    try:
        week_offset = int(request.args.get("week", 0))
    except ValueError:
        week_offset = 0

    today         = date.today()
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    end_of_week   = start_of_week + timedelta(days=6)

    meals = (
        MealLog.query
        .filter(
            MealLog.user_id == user_id,
            MealLog.date >= start_of_week,
            MealLog.date <= end_of_week
        )
        .order_by(MealLog.date.desc())
        .all()
    )
    total_cals = sum(log.food.calories for log in meals if log.food)

    form = MealForm()

    return render_template(
        'calorie_counter.html',
        form=form,
        meal_log=meals,
        total_calories=total_cals,
        week_offset=week_offset,
        start_of_week=start_of_week,
        end_of_week=end_of_week,
        date=date
    )


@app.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard.html')


@app.route('/refresh_scoreboard')
def refresh_scoreboard():
    user_id = session.get("user_id")
    if not user_id:
        return "Not logged in", 401

    user = User.query.get(user_id)
    if not user or not user.team:
        return render_template('partials/scoreboard.html', scoreboard=[])

    team_users = User.query.filter_by(team=user.team).all()
    scoreboard = []

    for teammate in team_users:
        today_logs = [log for log in teammate.exercise_logs if log.date == date.today()]
        today_meals = [log for log in teammate.meal_logs if log.date == date.today()]
        if not today_logs or not today_meals:
            continue

        total_burned = sum(log.calories_burned for log in today_logs)
        total_eaten = sum(log.meal.calories for log in today_meals)
        net = total_eaten - total_burned

        scoreboard.append({
            "user": teammate,
            "burned": total_burned,
            "eaten": total_eaten,
            "net": net
        })

    scoreboard.sort(key=lambda x: x["net"])
    return render_template('partials/scoreboard.html', scoreboard=scoreboard)


@app.route('/update_team', methods=['POST'])
def update_team():
    if "user_id" not in session:
        flash("You must be logged in to update your team.", "error")
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    new_team = request.form.get('team') or request.form.get('new_team')

    if not new_team or not new_team.strip():
        flash("Team name cannot be empty.", "warning")
        return redirect(url_for('dashboard'))

    cleaned_team = new_team.strip()

    if user.team == cleaned_team:
        flash(f"You're already in the team: {cleaned_team}", "info")
    else:
        user.team = cleaned_team
        db.session.commit()
        flash(f"You've joined the team: {cleaned_team}", "success")

    return redirect(url_for('dashboard'))


@app.route('/user/<int:user_id>')
def user_detail(user_id):
    if "user_id" not in session:
        flash("Please log in to view user profiles.", "error")
        return redirect(url_for("login"))

    selected_user = User.query.get_or_404(user_id)

    today = date.today()
    todays_exercises = ExerciseLog.query.filter_by(user_id=selected_user.id, date=today).all()
    todays_meals = [log for log in selected_user.meal_logs if log.date == today]

    week_start = today - timedelta(days=today.weekday())
    weekly_scores = Scoreboard.query.filter(
        Scoreboard.user_id == selected_user.id,
        Scoreboard.timestamp >= week_start,
        Scoreboard.timestamp <= today
    ).group_by(Scoreboard.timestamp).with_entities(
        Scoreboard.timestamp,
        func.sum(Scoreboard.total_calories_burned)
    ).all()

    week_data = {record[0].strftime('%a'): float(record[1]) for record in weekly_scores}
    labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    chart_data = [week_data.get(day, 0) for day in labels]

    return render_template("user_detail.html",
                           user=selected_user,
                           exercise_log=todays_exercises,
                           meal_log=todays_meals,
                           chart_data=chart_data,
                           date=date)

@app.route('/api/calorie-data')
def get_calorie_data():
    user_id = session.get("user_id")
    if not user_id:
        return {"error": "Not logged in"}, 401

    # Get week offset from URL (same logic as exercise_log)
    try:
        week_offset = int(request.args.get("week", 0))
    except ValueError:
        week_offset = 0

    today = date.today()
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    days = [start_of_week + timedelta(days=i) for i in range(7)]

    data = []
    for day in days:
        logs = MealLog.query.filter_by(user_id=user_id, date=day).all()
        total = sum(log.food.calories for log in logs if log.food)
        data.append({
            "label": day.strftime('%a'),
            "calories": total
        })
    return data

@app.route('/api/foods')
def foods_search():
    q = request.args.get('q', '').strip()
    if len(q) < 2:
        return jsonify([])

    # 1) Local DB search
    local = (
        Food.query
        .filter(Food.name.ilike(f"%{q}%"))
        .limit(10)
        .all()
    )
    results = [{
        'id':       f.id,
        'name':     f.name,
        'calories': f.calories,
        'serving':  f.serving_size
    } for f in local]

    # 2) Determine if we have a USDA key to use
    api_key = None
    # check per‐user key
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        api_key = user.usda_api_key
    # fallback to global
    if not api_key:
        api_key = current_app.config.get('FDC_API_KEY')

    # 3) Only call USDA if we still want more AND we have a key
    if api_key and len(results) < 10:
        # Temporarily inject the key into the USDA client
        # (or modify search_foods to accept a key param)
        current_app.config['FDC_API_KEY'] = api_key
        usda_hits = search_foods(q, page_size=10 - len(results))
        for item in usda_hits:
            calories = next(
                (nut['value'] for nut in item.get('foodNutrients', [])
                 if nut.get('nutrientName') == "Energy"),
                None
            )
            results.append({
                'fdcId':     item['fdcId'],
                'name':      item['description'],
                'calories':  calories,
                'serving':   item.get('servingSizeUnit', '100 g')
            })

    return jsonify(results)