'''
Sets up the Flask application.
Defines the /budget route to display the form and handle form submissions.
Prints form data to the terminal upon successful submission.
Redirects to the same page to clear the form and prevent resubmission issues.

To run the code, copy and paste this:
export SECRET_KEY=$(python -c 'import os; print(os.urandom(24))')
python3 app.py
'''

import os
from flask import Flask, render_template, redirect, url_for, flash
from forms import BudgetForm

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback_secret_key')

@app.route('/budget', methods=['GET', 'POST'])
def budget():
    form = BudgetForm()

    # Check if the form is submitted and validated
    if form.validate_on_submit():
        print(f"Housing and Utilities: {form.housing_utilities.data}")
        print(f"Communication: {form.communication.data}")
        print(f"Transportation: {form.transportation.data}")
        print(f"Education: {form.education.data}")
        print(f"Savings: {form.savings.data}")
        print(f"Food: {form.food.data}")
        print(f"Entertainment: {form.entertainment.data}")
        print(f"Health and Personal Care: {form.health_personal_care.data}")
        print(f"Clothing and Laundry: {form.clothing_laundry.data}")
        print(f"Debt Payments: {form.debt_payments.data}")

        flash('Budget information submitted successfully!', 'success')

        # Redirect to the same page to clear the form
        return redirect(url_for('budget'))

    # Render the budget_form.html template and pass the form to it
    return render_template('budget_form.html', title='Budget Form', form=form)

if __name__ == '__main__':
    app.run(debug=True)
