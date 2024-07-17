'''
Creates the form that will be used to collect budget information from the user
'''
from flask_wtf import FlaskForm
from wtforms import DecimalField, SubmitField
from wtforms.validators import InputRequired, NumberRange

class BudgetForm(FlaskForm):

    # Income Information
    income = DecimalField('What is your monthly income?', validators=[InputRequired(), NumberRange(min=0)])

    # Fixed Expenses
    housing_utilities = DecimalField('How much do you spend on rent or dorm fees, and utilities (electricity, gas, water) per month?', validators=[InputRequired(), NumberRange(min=0)])
    communication = DecimalField('How much is your monthly expense for cell phone and internet services?', validators=[InputRequired(), NumberRange(min=0)])
    transportation = DecimalField('What is your total monthly cost for transportation, including car-related expenses (insurance, maintenance, repairs, parking fees, loan payments) and public transportation?', validators=[InputRequired(), NumberRange(min=0)])
    education = DecimalField('What is your monthly cost for books and educational materials?', validators=[InputRequired(), NumberRange(min=0)])
    savings = DecimalField('How much money do you set aside for savings each month?', validators=[InputRequired(), NumberRange(min=0)])
    
    # Variable Expenses
    food = DecimalField('How much do you spend on groceries or a meal plan per month?', validators=[InputRequired(), NumberRange(min=0)])
    entertainment = DecimalField('What is your monthly expense for entertainment, including dining out, concerts, music downloads, and movies?', validators=[InputRequired(), NumberRange(min=0)])
    health_personal_care = DecimalField('What is your monthly cost for medical expenses, prescriptions, laundry/dry cleaning, and personal care expenses?', validators=[InputRequired(), NumberRange(min=0)])
    clothing_laundry = DecimalField('How much do you spend on clothing per month?', validators=[InputRequired(), NumberRange(min=0)])
    debt_payments = DecimalField('How much is your monthly payment for credit card debt?', validators=[InputRequired(), NumberRange(min=0)])
    
    # Submit button
    submit = SubmitField('Submit')
