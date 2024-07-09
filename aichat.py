import openai

openai.api_key = ''
model = "GPT-4o"

def chatbot():
    print("Welcome to the OpenAI Chatbot! Type 'exit' to end the conversation.")
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() == 'exit':
            print("Chatbot: Goodbye!")
            break

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a financial planner tasked with helping the user make smarter financial decisions"},
                {"role": "user", "content": user_input}
            ]
        )
        
        message = response['choices'][0]['message']['content'].strip()
        print(f"Chatbot: {message}")

if __name__ == "__main__":
    chatbot()

