'''
Creates the form that will be used to collect budget information from the user
'''

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from validators import NonNegativeFloat  # Import the custom validator

# Used the resource below to come up with the categories below:
# https://studentaid.gov/resources/prepare-for-college/students/budgeting/creating-your-budget

class BudgetForm(FlaskForm):
    # Fixed Expenses
    housing_utilities = StringField('How much do you spend on rent or dorm fees, and utilities (electricity, gas, water) per month?', validators=[DataRequired(), NonNegativeFloat])
    communication = StringField('How much is your monthly expense for cell phone and internet services?', validators=[DataRequired(), NonNegativeFloat])
    transportation = StringField('What is your total monthly cost for transportation, including car-related expenses (insurance, maintenance, repairs, parking fees, loan payments) and public transportation?', validators=[DataRequired(), NonNegativeFloat])
    education = StringField('What is your monthly cost for books and educational materials?', validators=[DataRequired(), NonNegativeFloat])
    savings = StringField('How much money do you set aside for savings each month?', validators=[DataRequired(), NonNegativeFloat])
    
    # Variable Expenses
    food = StringField('How much do you spend on groceries and dining out per month?', validators=[DataRequired(), NonNegativeFloat])
    entertainment = StringField('What is your monthly expense for entertainment, including concerts, music downloads, and movies?', validators=[DataRequired(), NonNegativeFloat])
    health_personal_care = StringField('What is your monthly cost for medical expenses, prescriptions, hair, nails, and health club memberships?', validators=[DataRequired(), NonNegativeFloat])
    clothing_laundry = StringField('How much do you spend on clothing and laundry/dry cleaning per month?', validators=[DataRequired(), NonNegativeFloat])
    debt_payments = StringField('How much is your monthly payment for credit card debt?', validators=[DataRequired(), NonNegativeFloat])
    
    # Submit button
    submit = SubmitField('Submit')