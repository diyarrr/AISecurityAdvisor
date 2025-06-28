from flask import Flask, request, jsonify, session
from flask_cors import CORS
import os
from dotenv import load_dotenv
import json
from models import User
from chatbot import SecurityChatbot
from retriever import DocumentRetriever

# Load environment variables
load_dotenv(dotenv_path="config/.env", override=True)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")
CORS(app,
     supports_credentials=True,
     origins=["http://localhost:3000"],
     methods=["GET", "POST", "OPTIONS"],
     allow_headers=["Content-Type"])

# Initialize retriever and chatbot
retriever = DocumentRetriever()
chatbot = SecurityChatbot(retriever)

# In-memory user storage for prototype
# In production, use a proper database
users = {}


def get_current_user():
    user_id = session.get('user_id')
    if not user_id or user_id not in users:
        return None
    return users[user_id]


@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
    
    # Create user if doesn't exist
    if user_id not in users:
        users[user_id] = User(user_id)
    
    session['user_id'] = user_id
    return jsonify({
        "message": "Login successful",
        "user": users[user_id].to_dict()
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    query = data.get("query")
    user = get_current_user()  # Assuming this gets user from session

    if not user:
        return jsonify({"error": "Not logged in"}), 401

    if not chatbot.check_topic_access(query, user.rank):
        return jsonify({"answer": "This topic is restricted based on your current rank.", "restricted": True})

    answer = chatbot.generate_response(query, user.rank)

    # Generate follow-up quiz
    followup = chatbot.generate_followup_question(answer)

    return jsonify({
        "answer": answer,
        "followup_question": followup,
        "user": user.to_dict(),
        "restricted": False
    })

@app.route('/api/quiz', methods=['POST'])
def quiz():
    data = request.get_json()
    user_answer = data.get("answer", "").strip().lower()
    correct_answer = data.get("correct_answer", "").strip().lower()
    user = get_current_user()

    if not user:
        return jsonify({"error": "Not logged in"}), 401

    if user_answer == correct_answer:
        xp = 50
        user.add_xp(xp)
        return jsonify({
            "correct": True,
            "xp_gained": xp,
            "user": user.to_dict()
        })
    else:
        penalty = 10
        user.add_xp(-penalty)
        return jsonify({
            "correct": False,
            "xp_gained": -penalty,
            "user": user.to_dict()
        })

if __name__ == '__main__':
    app.run(port=8000,debug=True)