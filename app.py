'''
Sets up the Flask application.
Defines the /budget route to display the form and handle form submissions.
Prints form data to the terminal upon successful submission.
Redirects to the same page to clear the form and prevent resubmission issues.

To run the code, copy and paste this:
export SECRET_KEY=$(python3 -c 'import os; print(os.urandom(24))')
python3 app.py
'''

import os
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from forms import BudgetForm
import openai

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback_secret_key')

openai.api_key = ""

@app.route('/', methods=['GET', 'POST'])
def home():
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
        return render_template('home.html', form=form, income=income, expenses=expenses, percentages=percentages, ideal_amounts=ideal_amounts)
    return render_template('home.html', form=form)

@app.route('/chatbox')
def chatbot_site():
    return render_template('chatbot.html')

@app.route('/chat', methods=['POST'])
def chatbot():
    user_input = request.json.get('message')
    
    if user_input.lower() == 'exit':
        response = {"message": "Goodbye!"}
    else:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a financial planner tasked with helping the user make smarter financial decisions. Limit your responses to 500 characters"},
                    {"role": "user", "content": user_input}
                ]
            )
            message = response['choices'][0]['message']['content'].strip()
            response = {"message": message}
        except Exception as e:
            response = {"message": "Something went wrong"}
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
