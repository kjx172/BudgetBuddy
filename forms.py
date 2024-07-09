'''
Creates the form that will be used to collect budget information from the user
'''
from flask_wtf import FlaskForm
from wtforms import DecimalField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class BudgetForm(FlaskForm):

    # Income Information
    income = DecimalField('What is your monthly income?', validators=[DataRequired(), NumberRange(min=0)])

    # Fixed Expenses
    housing_utilities = DecimalField('How much do you spend on rent or dorm fees, and utilities (electricity, gas, water) per month?', validators=[DataRequired(), NumberRange(min=0)])
    communication = DecimalField('How much is your monthly expense for cell phone and internet services?', validators=[DataRequired(), NumberRange(min=0)])
    transportation = DecimalField('What is your total monthly cost for transportation, including car-related expenses (insurance, maintenance, repairs, parking fees, loan payments) and public transportation?', validators=[DataRequired(), NumberRange(min=0)])
    education = DecimalField('What is your monthly cost for books and educational materials?', validators=[DataRequired(), NumberRange(min=0)])
    savings = DecimalField('How much money do you set aside for savings each month?', validators=[DataRequired(), NumberRange(min=0)])
    
    # Variable Expenses
    food = DecimalField('How much do you spend on groceries and dining out per month?', validators=[DataRequired(), NumberRange(min=0)])
    entertainment = DecimalField('What is your monthly expense for entertainment, including concerts, music downloads, and movies?', validators=[DataRequired(), NumberRange(min=0)])
    health_personal_care = DecimalField('What is your monthly cost for medical expenses, prescriptions, hair, nails, and health club memberships?', validators=[DataRequired(), NumberRange(min=0)])
    clothing_laundry = DecimalField('How much do you spend on clothing and laundry/dry cleaning per month?', validators=[DataRequired(), NumberRange(min=0)])
    debt_payments = DecimalField('How much is your monthly payment for credit card debt?', validators=[DataRequired(), NumberRange(min=0)])
    
    # Submit button
    submit = SubmitField('Submit')
