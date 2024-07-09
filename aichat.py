import openai

def generate_response(user_input):
    response = openai.ChatCompletion.create(
        model=OpenAIBot.model,
        messages=[
            {"role": "system", "content": "You are a financial planner tasked with helping the user make smarter financial decisions. Keep your responses under 500 characters."},
            {"role": "user", "content": user_input}
            ])
        message = response['choices'][0]['message']['content'].strip()
        return message
class OpenAIBot:
    openai.api_key = "sk-proj-Oo0wuqcepxoAVDOiYiIuT3BlbkFJ0D0y57uNzQhTS7a3teN5"
    model = "GPT-4o"

    def generate_response():
        print("Hello! I am your financial planner! How can I help? (Type 'exit' to end the conversation)")
        
        while True:
            user_input = input("You: ")
            
            if user_input.lower() == 'exit':
                print("Chatbot: Goodbye!")
                break

            response = openai.ChatCompletion.create(
                model= "gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a financial planner tasked with helping the user make smarter financial decisions"},
                    {"role": "system", "content": "Keep your responses under 500 characters"},
                    {"role": "user", "content": user_input}
                ]
            )

            message = response['choices'][0]['message']['content'].strip()
            print(f"Chatbot: {message}")


