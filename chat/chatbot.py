from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

def load_responses():
    if os.path.exists('responses.json'):
        with open('responses.json', 'r') as file:
            return json.load(file)
    return {}

def save_responses(responses):
    with open('responses.json', 'w') as file:
        json.dump(responses, file, indent=4)

@app.route('/')
def index():
    return render_template('indexS.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.form['user_input'].lower()
    responses = load_responses()
    bot_response = ''

    if user_input == 'quit':
        bot_response = "Goodbye!"
    elif user_input in responses:
        bot_response = responses[user_input]
    else:
        # Store unknown question to a JSON file
        store_unknown_question(user_input)
        bot_response = "Sorry, I don't know the answer to that question."

    return jsonify({'bot_response': bot_response})

def store_unknown_question(question):
    unknown_questions = load_unknown_questions()
    unknown_questions.append(question)
    save_unknown_questions(unknown_questions)

def load_unknown_questions():
    if os.path.exists('unknown_questions.json'):
        with open('unknown_questions.json', 'r') as file:
            return json.load(file)
    return []

def save_unknown_questions(unknown_questions):
    with open('unknown_questions.json', 'w') as file:
        json.dump(unknown_questions, file, indent=4)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5200, debug=False)
