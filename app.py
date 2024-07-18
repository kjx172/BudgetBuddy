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

# Function to generate a random secret key
def generate_random_key(length=24):
    alphabet = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
    return ''.join(secrets.choice(alphabet) for _ in range(length))

# Ensure the api_key is provided
if not api_key:
    raise ValueError("No API key found. Please set the OPENAI_API_KEY environment variable.")

#connects to the chatgpt api
client = OpenAI(api_key=api_key)

app = Flask(__name__)

#configures the secret key to be random and connecting database.db to SQLalchamey
app.config['SECRET_KEY'] = generate_random_key()
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"

#creates a database for the app, checks if passwords match
db = SQLAlchemy(app)
with app.app_context():
    db.create_all()
    print("Database tables created.")
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

def validate_username(username):
    existing_user_username = User.query.filter_by(username=username).first()
    if not existing_user_username:
        return True

# Function to create the database table
def create_table():
    conn = sqlite3.connect('budgetbuddy.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS budget (
            id INTEGER PRIMARY KEY,
            income REAL,
            housing_utilities REAL,
            communication REAL,
            transportation REAL,
            education REAL,
            savings REAL,
            food REAL,
            entertainment REAL,
            health_personal_care REAL,
            clothing_laundry REAL,
            debt_payments REAL
        )
    ''')
    conn.commit()
    conn.close()

# Function to insert data into the database
def insert_budget_data(form_data):
    conn = sqlite3.connect('budgetbuddy.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO budget (income, housing_utilities, communication, transportation, education, savings, food, entertainment, health_personal_care, clothing_laundry, debt_payments)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', [float(data) for data in form_data])
    conn.commit()
    conn.close()

def get_last_row():
    conn = sqlite3.connect("budgetbuddy.db")
    c = conn.cursor()
    c.execute('SELECT * FROM budget ORDER BY id DESC LIMIT 1')
    last_row = c.fetchone()
    conn.close()
    return last_row

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        form_type = request.form.get('form_type')

        if form_type == 'sign-up':  # Check if sign-up form is submitted
            # hashes password and uses that + username to store user in db

            #if username already exists
            if not validate_username(username):
                flash('Username is already in use.')
                return redirect(url_for('login'))
            
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()

            flash('Account created successfully. Please log in.')
            return redirect(url_for('login'))

        elif form_type == 'log-in':
            # Retrieve the user from the database
            user = User.query.filter_by(username=username).first()

            #if the username is valid and the password entered matches the username's hashed password
            if user and bcrypt.check_password_hash(user.password, password):
                session['user_id'] = user.id
                return redirect(url_for('form'))
            else:
                flash('Invalid credentials. Please try again.')

    return render_template('login.html')

@app.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html')

@app.route('/form', methods=['GET', 'POST'])
@login_required
def form():        
    form = BudgetForm()
    if form.validate_on_submit():
        income = float(form.income.data)
        expenses = {
            'Needs': float(form.housing_utilities.data) + float(form.food.data) + float(form.transportation.data) + float(form.communication.data) + float(form.education.data) + float(form.health_personal_care.data),
            'Wants': float(form.entertainment.data) + float(form.clothing_laundry.data),
            'Savings or Debt Repayment': float(form.savings.data) + float(form.debt_payments.data)
        }
        percentages = {category: (amount / income) * 100 for category, amount in expenses.items()}
        ideal_amounts = {
            'Needs': income * 0.50,
            'Wants': income * 0.30,
            'Savings or Debt Repayment': income * 0.20
        }

        # Insert data into the database
        form_data = (
            form.income.data,
            form.housing_utilities.data,
            form.communication.data,
            form.transportation.data,
            form.education.data,
            form.savings.data,
            form.food.data,
            form.entertainment.data,
            form.health_personal_care.data,
            form.clothing_laundry.data,
            form.debt_payments.data
        )
        insert_budget_data(form_data)
        # Redirect to the summary page
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
        last_row = get_last_row()
        if last_row:
            income = last_row[1]
            expenses = last_row[2:]
            initial_message = f"User's income: ${income:.2f}\n" \
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
            initial_message = "The user hasn't filled out the form on the home page yet. Suggest the user fill out the form."

        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Your name is Bud. You are a financial planner tasked with helping the user make smarter financial decisions."},
                    {"role": "system", "content": "Introduce yourself only on the first message."},
                    {"role": "system", "content": "Limit your responses to 500 characters"}, 
                    {"role": "system", "content": "Be friendly and make sure your responses are clear and simple. Someone with no financial knowledge should understand."},
                    {"role": "system", "content": "Your audience is college students. Tailor your responses to the finances and situations of the typical American college student."},
                    {"role": "system", "content": "Offer practical tips and examples whenever possible."},
                    {"role": "system", "content": initial_message},
                    {"role": "system", "content": "Remember that housing and utilities, communication, transportation, education, food, and health and personal care expenses are the user's needs. Entertainment and clothing expenses are the user's wants. Debt payment and saving expenses are the user's savings/debt repayments."},
                    {"role": "system", "content": "If the user asks about budgeting, tell them about the 50/20/30 budget rule."},
                    {"role": "system", "content": "Ideally, the user should allocate 50% of their income to their needs, 30% to their wants, and 20% to their savings and debt repayments."},
                    {"role": "system", "content": "When responding to the user, consider the user's income and expense information."},
                    {"role": "user", "content": user_input}
                ]
            )
            message = response.choices[0].message.content.strip()
            response = {"message": message}
        except Exception as e:
            # Log the error message to understand what went wrong
            print(f"Error: {str(e)}")
            response = {"message": "Something went wrong"}

    return jsonify(response)

@app.route('/summary')
@login_required
def summary():
    last_row = get_last_row()
    if last_row:
        income = last_row[1]
        expenses = last_row[2:]

        needs = expenses[0] + expenses[5] + expenses[2] + expenses[1] + expenses[3] + expenses[7]
        wants = expenses[6] + expenses[8]
        savings_or_debt = expenses[4] + expenses[9]

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
        expenses = []
        actual_amounts = {'Needs': 0, 'Wants': 0, 'Savings or Debt Repayment': 0}
        actual_percentages = {'Needs': 0, 'Wants': 0, 'Savings or Debt Repayment': 0}
        ideal_amounts = {'Needs': 0, 'Wants': 0, 'Savings or Debt Repayment': 0}
        ideal_percentages = {'Needs': 0, 'Wants': 0, 'Savings or Debt Repayment': 0}

    return render_template('summary.html', income=income, expenses = expenses, actual_amounts = actual_amounts, actual_percentages=actual_percentages, ideal_amounts=ideal_amounts, ideal_percentages=ideal_percentages)

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
    create_table()  # Create the database table if it doesn't exist
    app.run(debug=True)
