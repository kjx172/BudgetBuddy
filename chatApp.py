from flask import Flask, render_template, request, jsonify
import openai

openai.api_key = "sk-proj-Oo0wuqcepxoAVDOiYiIuT3BlbkFJ0D0y57uNzQhTS7a3teN5"

# Creating the Flask App
app = Flask(__name__)

@app.route('/')
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
    app.run(debug=True, host="0.0.0.0")

