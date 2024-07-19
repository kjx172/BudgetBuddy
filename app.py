import os
import sqlite3
from flask import Flask, render_template, redirect, url_for, request, jsonify, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from flask_bcrypt import Bcrypt
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from forms import BudgetForm
from openai import OpenAI
import git
import string
import secrets
from functools import wraps
from dotenv import load_dotenv
load_dotenv()

# Fetch the API key from the environment variable
api_key = os.getenv('OPENAI_API_KEY')

# Ensure the api_key is provided
if not api_key:
    raise ValueError("No API key found. Please set the OPENAI_API_KEY environment variable.")

#connects to the chatgpt api
client = OpenAI(api_key=api_key)

app = Flask(__name__)

#configures the secret key to be random and connecting database.db to SQLalchamey
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"

#creates a database for the app, checks if passwords match
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

#makes pages login restricted
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    financial_discipline = db.Column(db.String(100), nullable=False)
    spending_habits = db.Column(db.String(100), nullable=False)
    saving_importance = db.Column(db.String(100), nullable=False)
    short_term_savings = db.Column(db.Float, nullable=False)
    long_term_savings = db.Column(db.Float, nullable=False)
    investments = db.Column(db.Float, nullable=False)
    income = db.Column(db.Float, nullable=False)
    housing_utilities = db.Column(db.Float, nullable=False)
    communication = db.Column(db.Float, nullable=False)
    transportation = db.Column(db.Float, nullable=False)
    education = db.Column(db.Float, nullable=False)
    savings = db.Column(db.Float, nullable=False)
    food = db.Column(db.Float, nullable=False)
    entertainment = db.Column(db.Float, nullable=False)
    health_personal_care = db.Column(db.Float, nullable=False)
    clothing_laundry = db.Column(db.Float, nullable=False)
    debt_payments = db.Column(db.Float, nullable=False)

def validate_username(username):
    existing_user_username = User.query.filter_by(username=username).first()
    if not existing_user_username:
        return True


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        form_type = request.form.get('form_type')

        if form_type == 'sign-up':  # Check if sign-up form is submitted
            #if username already exists
            if not validate_username(username):
                flash('Username is already in use.', 'error')
                return redirect(url_for('login'))
            
            # hashes password and uses that + username to store user in db
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()

            flash('Account created successfully. Please log in.', 'info')
            return redirect(url_for('login'))

        elif form_type == 'log-in':
            # Retrieve the user from the database
            user = User.query.filter_by(username=username).first()

            #if the username is valid and the password entered matches the username's hashed password
            if user and bcrypt.check_password_hash(user.password, password):
                login_user(user)
                session['user_id'] = user.id
                print(f"Logged in user ID: {current_user.id}")
                return redirect(url_for('form'))
            else:
                flash('Invalid credentials. Please try again.', 'error')

    return render_template('login.html')


@app.route('/form', methods=['GET', 'POST'])
@login_required
def form():
    form = BudgetForm()
    if form.validate_on_submit():
        budget = Budget(
            user_id=current_user.id,
            age=form.age.data,
            financial_discipline=form.financial_discipline.data,
            spending_habits=form.spending_habits.data,
            saving_importance=form.saving_importance.data,
            short_term_savings=form.short_term_savings.data,
            long_term_savings=form.long_term_savings.data,
            investments=form.investments.data,
            income=form.income.data,
            housing_utilities=form.housing_utilities.data,
            communication=form.communication.data,
            transportation=form.transportation.data,
            education=form.education.data,
            savings=form.savings.data,
            food=form.food.data,
            entertainment=form.entertainment.data,
            health_personal_care=form.health_personal_care.data,
            clothing_laundry=form.clothing_laundry.data,
            debt_payments=form.debt_payments.data,
        )

        db.session.add(budget)
        db.session.commit()

        return redirect(url_for('summary'))
    return render_template('form.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/chatbot')
@login_required
def chatbot_site():
    return render_template('chatbot.html')

@app.route('/chat', methods=['POST'])
@login_required
def chatbot():
    user_input = request.json.get('message')

    if user_input.lower() == 'exit':
        response = {"message": "Goodbye!"}
    else:
        last_budget = Budget.query.filter_by(user_id=current_user.id).order_by(Budget.id.desc()).first()
        if last_budget:
            personality = [
                last_budget.age,
                last_budget.financial_discipline,
                last_budget.spending_habits,
                last_budget.saving_importance
            ]
            financial_history = [
                last_budget.short_term_savings,
                last_budget.long_term_savings,
                last_budget.investments
            ]
            income = last_budget.income
            expenses = [
                last_budget.housing_utilities,
                last_budget.communication,
                last_budget.transportation,
                last_budget.education,
                last_budget.savings,
                last_budget.food,
                last_budget.entertainment,
                last_budget.health_personal_care,
                last_budget.clothing_laundry,
                last_budget.debt_payments
            ]
            initial_message = f"User's age: {personality[0]}\n" \
                              f"How often does the user follow a budget?: {personality[1]}\n" \
                              f"How would the user describe their spending habits?: {personality[2]}\n" \
                              f"How important is it for the user to save a portion of their income regularly: {personality[3]}\n" \
                              f"The user's short-term savings: ${financial_history[0]:.2f}\n" \
                              f"The user's long-term savings: ${financial_history[1]:.2f}\n" \
                              f"The money the user currently has invested: ${financial_history[2]:.2f}\n" \
                              f"User's monthly income: ${income:.2f}\n" \
                              f"Housing and Utilities expenses: ${expenses[0]:.2f}\n" \
                              f"Communication expenses: ${expenses[1]:.2f}\n" \
                              f"Transportation expenses: ${expenses[2]:.2f}\n" \
                              f"Education expenses: ${expenses[3]:.2f}\n" \
                              f"Savings expenses: ${expenses[4]:.2f}\n" \
                              f"Food expenses: ${expenses[5]:.2f}\n" \
                              f"Entertainment expenses: ${expenses[6]:.2f}\n" \
                              f"Health and Personal Care expenses: ${expenses[7]:.2f}\n" \
                              f"Clothing expenses: ${expenses[8]:.2f}\n" \
                              f"Debt Payments expenses: ${expenses[9]:.2f}\n"
            
        else:
            initial_message = "The user hasn't filled out the form yet."

        prompt = initial_message + "The user says: " + user_input + " How do you respond?"

        response = client.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=150,
        )
        response = {"message": response.choices[0].text.strip()}

    return jsonify(response)

@app.route('/summary')
@login_required
def summary():
    last_budget = Budget.query.filter_by(user_id=current_user.id).order_by(Budget.id.desc()).first()

    if last_budget:
        income = last_budget.income
        expenses = [
            last_budget.housing_utilities,
            last_budget.communication,
            last_budget.transportation,
            last_budget.education,
            last_budget.savings,
            last_budget.food,
            last_budget.entertainment,
            last_budget.health_personal_care,
            last_budget.clothing_laundry,
            last_budget.debt_payments
        ]
        financial_history = [
            last_budget.short_term_savings,
            last_budget.long_term_savings,
            last_budget.investments
        ]

        needs = sum([expenses[0], expenses[5], expenses[2], expenses[1], expenses[3], expenses[7]])
        wants = sum([expenses[6], expenses[8]])
        savings_or_debt = sum([expenses[4], expenses[9]])

        actual_amounts = {
            'Needs': needs,
            'Wants': wants,
            'Savings or Debt Repayment': savings_or_debt
        }

        actual_percentages = {
            'Needs': round((needs / income) * 100, 2) if income > 0 else 0,
            'Wants': round((wants / income) * 100, 2) if income > 0 else 0,
            'Savings or Debt Repayment': round((savings_or_debt / income) * 100, 2) if income > 0 else 0
        }

        ideal_amounts = {
            'Needs': income * 0.50,
            'Wants': income * 0.30,
            'Savings or Debt Repayment': income * 0.20
        }

        ideal_percentages = {
            'Needs': 50,
            'Wants': 30,
            'Savings or Debt Repayment': 20
        }
    else:
        income = 0
        expenses = [0] * 10  # Default empty expenses list
        financial_history = [0] * 3  # Default empty financial history
        actual_amounts = {'Needs': 0, 'Wants': 0, 'Savings or Debt Repayment': 0}
        actual_percentages = {'Needs': 0, 'Wants': 0, 'Savings or Debt Repayment': 0}
        ideal_amounts = {'Needs': 0, 'Wants': 0, 'Savings or Debt Repayment': 0}
        ideal_percentages = {'Needs': 0, 'Wants': 0, 'Savings or Debt Repayment': 0}

    return render_template('summary.html', income=income, expenses=expenses, financial_history=financial_history, actual_amounts=actual_amounts, actual_percentages=actual_percentages, ideal_amounts=ideal_amounts, ideal_percentages=ideal_percentages)

@app.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html')


@app.route("/update_server", methods=['POST'])
def webhook():
    if request.method == 'POST':
        repo = git.Repo('/home/BudgetBuddy12345/BudgetBuddy')
        origin = repo.remotes.origin
        origin.pull()
        return 'Updated PythonAnywhere successfully', 200
    else:
        return 'Wrong event type', 400


if __name__ == '__main__':
    app.run(debug=True)
