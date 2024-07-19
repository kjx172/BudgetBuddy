import os
import sqlite3
from flask import Flask, render_template, redirect, url_for, request, jsonify, flash
from forms import BudgetForm
from openai import OpenAI
import git
import string
import secrets
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

client = OpenAI(api_key=api_key)

app = Flask(__name__)
app.config['SECRET_KEY'] = generate_random_key()

# Function to create the database table
def create_table():
    conn = sqlite3.connect('budgetbuddy.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS budget (
            id INTEGER PRIMARY KEY,
            age INTEGER,
            financial_discipline TEXT,
            spending_habits TEXT,
            saving_importance TEXT,
            short_term_savings REAL,
            long_term_savings REAL,
            investments REAL,
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
        INSERT INTO budget (age, financial_discipline, spending_habits, saving_importance, short_term_savings, long_term_savings, investments, income, housing_utilities, communication, transportation, education, savings, food, entertainment, health_personal_care, clothing_laundry, debt_payments)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', [
        int(form_data['age']),
        form_data['financial_discipline'],
        form_data['spending_habits'],
        form_data['saving_importance'],
        float(form_data['short_term_savings']),
        float(form_data['long_term_savings']),
        float(form_data['investments']),
        float(form_data['income']),
        float(form_data['housing_utilities']),
        float(form_data['communication']),
        float(form_data['transportation']),
        float(form_data['education']),
        float(form_data['savings']),
        float(form_data['food']),
        float(form_data['entertainment']),
        float(form_data['health_personal_care']),
        float(form_data['clothing_laundry']),
        float(form_data['debt_payments'])
    ])
    conn.commit()
    conn.close()

def get_last_row():
    conn = sqlite3.connect("budgetbuddy.db")
    c = conn.cursor()
    c.execute('SELECT * FROM budget ORDER BY id DESC LIMIT 1')
    last_row = c.fetchone()
    conn.close()
    return last_row

@app.route('/home', methods=['GET', 'POST'])
def home():
    form = BudgetForm()
    if form.validate_on_submit():
        form_data = {
            'age': form.age.data,
            'financial_discipline': form.financial_discipline.data,
            'spending_habits': form.spending_habits.data,
            'saving_importance': form.saving_importance.data,
            'short_term_savings': form.short_term_savings.data,
            'long_term_savings': form.long_term_savings.data,
            'investments': form.investments.data,
            'income': form.income.data,
            'housing_utilities': form.housing_utilities.data,
            'communication': form.communication.data,
            'transportation': form.transportation.data,
            'education': form.education.data,
            'savings': form.savings.data,
            'food': form.food.data,
            'entertainment': form.entertainment.data,
            'health_personal_care': form.health_personal_care.data,
            'clothing_laundry': form.clothing_laundry.data,
            'debt_payments': form.debt_payments.data,
        }
        insert_budget_data(form_data)
        return redirect(url_for('summary'))

    return render_template('home.html', form=form)

@app.route('/chatbot')
def chatbot_site():
    return render_template('chatbot.html')

@app.route('/chat', methods=['POST'])
def chatbot():
    user_input = request.json.get('message')

    if user_input.lower() == 'exit':
        response = {"message": "Goodbye!"}
    else:
        last_row = get_last_row()
        if last_row:
            personality = last_row[1:5] 
            financial_history = [float(exp) for exp in last_row[5:8]]
            income = float(last_row[8])
            expenses = [float(exp) for exp in last_row[9:19]]
            
            initial_message = f"User's age: ${personality[0]:.2f}\n" \
                              f"How often does the user follow a budget?: {personality[1]}\n" \
                              f"How would the user describe their spending habits?: {personality[2]}\n" \
                              f"How important is it for the user to save a portion of your income regularly: {personality[3]}\n" \
                              f"The user's short-term savings (the money they have saved for expenses they'll face within the next year (e.g., groceries, textbooks, or travel)): ${financial_history[0]:.2f}\n" \
                              f"The user's long-term savings (the money they have saved for goals more than a year away (e.g., savings for post-graduation plans, a car, or future investments)): ${financial_history[1]:.2f}\n" \
                              f"The money the user currently has invested (e.g., in stocks, bonds, or mutual funds): ${financial_history[2]:.2f}\n" \
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
            initial_message = "The user hasn't filled out the form on the home page yet. Suggest the user fill out the form."

        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Your name is Bud. You are a financial planner tasked with helping the user make smarter financial decisions."},
                    {"role": "system", "content": "Introduce yourself only on the first message."},
                    {"role": "system", "content": "Limit your responses to 500 characters"}, 
                    {"role": "system", "content": "Be friendly and make sure your responses are clear and simple. Someone with no financial knowledge should understand."},
                    {"role": "system", "content": "Offer practical tips and examples whenever possible."},
                    {"role": "system", "content": initial_message},
                    {"role": "system", "content": "Your audience is college students. Tailor your responses to the finances and situations of the typical American college student."},
                    {"role": "system", "content": "Remember that housing and utilities, communication, transportation, education, food, and health and personal care expenses are the user's needs. Entertainment and clothing expenses are the user's wants. Debt payment and saving expenses are the user's savings/debt repayments."},
                    {"role": "system", "content": "If the user asks about budgeting, tell them about the 50/30/20 budget rule."},
                    {"role": "system", "content": "Ideally, the user should allocate 50% of their income to their needs, 30% to their wants, and 20% to their savings and debt repayments."},
                    {"role": "system", "content": "When responding to the user, consider the user's age, short and long term savings, investments, income, and expense information."},
                    {"role": "system", "content": "If the user asks advice about something they want to buy, pay attention to the user's short and long term savings in addition to their expenses and income."},
                    {"role": "user", "content": user_input}
                ]
            )
            message = response.choices[0].message.content.strip()
            response = {"message": message}
        except Exception as e:
            print(f"Error: {str(e)}")
            response = {"message": "Something went wrong"}

    return jsonify(response)

@app.route('/summary')
def summary():
    last_row = get_last_row()
    if last_row:
        income = float(last_row[8])
        expenses = last_row[9:19]
        financial_history = last_row[5:8]

        needs = sum([float(expenses[0]), float(expenses[5]), float(expenses[2]), float(expenses[1]), float(expenses[3]), float(expenses[7])])
        wants = sum([float(expenses[6]), float(expenses[8])])
        savings_or_debt = sum([float(expenses[4]), float(expenses[9])])

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

    return render_template('summary.html', income=income, expenses=expenses, financial_history=financial_history, actual_amounts=actual_amounts, actual_percentages=actual_percentages, ideal_amounts=ideal_amounts, ideal_percentages=ideal_percentages)


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

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
    create_table()  # Create the database table if it doesn't exist
    app.run(debug=True)
