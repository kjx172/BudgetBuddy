'''
Creates the form that will be used to collect budget information from the user
'''
from flask_wtf import FlaskForm
from wtforms import DecimalField, SubmitField, RadioField, IntegerField
from wtforms.validators import InputRequired, NumberRange

class BudgetForm(FlaskForm):

    # Financial Personality
    age = IntegerField('How old are you?', validators=[InputRequired(), NumberRange(min=0)])
    financial_discipline = RadioField('How often do you follow a budget?', choices=[('Always', 'Always'), ('Sometimes', 'Sometimes'), ('Rarely', 'Rarely')], validators=[InputRequired()])
    spending_habits = RadioField('How would you describe your spending habits?', choices=[('Save more than I spend', 'I usually save more than I spend'), ('Spend and save in balance', 'I spend and save in balance'), ('Spend more than I save', 'I often spend more than I save')], validators=[InputRequired()])
    saving_importance = RadioField('How important is it for you to save a portion of your income regularly?', choices=[('Very important', 'Very important'), ('Somewhat important', 'Somewhat important'), ('Not important', 'Not important')], validators=[InputRequired()])

    # Financial History
    short_term_savings = DecimalField("How much money do you have saved for expenses you'll face within the next year?", validators=[InputRequired(), NumberRange(min=0)])
    long_term_savings = DecimalField("How much money do you have saved for goals more than a year away?", validators=[InputRequired(), NumberRange(min=0)])
    investments = DecimalField("How much money do you currently have invested?", validators=[InputRequired(), NumberRange(min=0)])

    # Monthly Income Information
    income = DecimalField('What is your monthly income?', validators=[InputRequired(), NumberRange(min=0)])
    
    # Fixed Expenses
    housing_utilities = DecimalField('How much do you spend on rent or dorm fees, and utilities per month?', validators=[InputRequired(), NumberRange(min=0)])
    communication = DecimalField('How much is your monthly expense for cell phone and internet services?', validators=[InputRequired(), NumberRange(min=0)])
    transportation = DecimalField('What is your total monthly cost for transportation, including car-related expenses and public transportation?', validators=[InputRequired(), NumberRange(min=0)])
    education = DecimalField('What is your monthly cost for books and educational materials?', validators=[InputRequired(), NumberRange(min=0)])
    savings = DecimalField('How much money do you set aside for savings each month?', validators=[InputRequired(), NumberRange(min=0)])
    
    # Variable Expenses
    food = DecimalField('How much do you spend on groceries or a meal plan per month?', validators=[InputRequired(), NumberRange(min=0)])
    entertainment = DecimalField('What is your monthly expense for entertainment?', validators=[InputRequired(), NumberRange(min=0)])
    health_personal_care = DecimalField('What is your monthly cost for medical expenses, prescriptions, laundry/dry cleaning, and personal care expenses?', validators=[InputRequired(), NumberRange(min=0)])
    clothing_laundry = DecimalField('How much do you spend on clothing per month?', validators=[InputRequired(), NumberRange(min=0)])
    debt_payments = DecimalField('How much is your monthly payment for debt?', validators=[InputRequired(), NumberRange(min=0)])

    # Submit button
    submit = SubmitField('Submit')