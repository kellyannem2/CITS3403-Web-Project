# forms.py
from flask_wtf import FlaskForm
from wtforms import DateTimeLocalField, StringField, IntegerField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Optional
from datetime import datetime

class MealForm(FlaskForm):
    meal_date_time = DateTimeLocalField(
        'Date/Time',
        default=datetime.now,
        format='%Y-%m-%dT%H:%M',
        validators=[DataRequired()]
    )
    search_food       = StringField('Search Food', validators=[Optional()])
    selected_food_id  = HiddenField()
    selected_food_cal = HiddenField()
    fdc_id            = HiddenField() 
    custom_name       = StringField('Food name')
    custom_calories   = IntegerField('Calories')
    submit_choose     = SubmitField('Add Meal')
    submit_custom     = SubmitField('Add Meal')
