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
from flask import Flask, render_template, redirect, url_for, flash, request
from forms import BudgetForm

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback_secret_key')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/budget_form', methods=['GET', 'POST'])
def budget_form():
    form = BudgetForm()
    if form.validate_on_submit():
        # Collect the data and redirect to the summary page with the data
        return redirect(url_for('budget_summary', 
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
                                debt_payments=form.debt_payments.data))
    return render_template('budget_form.html', form=form)

@app.route('/budget_summary')
def budget_summary():
    income = float(request.args.get('income'))
    expenses = {
        'Needs': float(request.args.get('housing_utilities')) + float(request.args.get('food')) + float(request.args.get('transportation')) + float(request.args.get('communication')) + float(request.args.get('education')) + float(request.args.get('health_personal_care')),
        'Wants': float(request.args.get('entertainment')) + float(request.args.get('clothing_laundry')),
        'Savings or Debt Repayment': float(request.args.get('savings')) + float(request.args.get('debt_payments'))
    }
    percentages = {category: (amount / income) * 100 for category, amount in expenses.items()}
    ideal_amounts = {
        'Needs': income * 0.50,
        'Wants': income * 0.30,
        'Savings or Debt Repayment': income * 0.20
    }
    return render_template('summary.html', percentages=percentages, ideal_amounts=ideal_amounts, expenses=expenses, income=income)

if __name__ == '__main__':
    app.run(debug=True)
