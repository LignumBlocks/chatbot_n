from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import os
from dotenv import load_dotenv

from chatbot import WoodxelChatbot, LignumChatbot, LLM

load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', os.urandom(32).hex())
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    # 'JWT_TOKEN_LOCATION': ['headers', 'cookies'],
    # 'JWT_COOKIE_SECURE': True,
    # 'JWT_COOKIE_SAMESITE': 'Lax'
    
# Initialize JWT Manager
jwt = JWTManager(app)

# Security configuration
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['REMEMBER_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True

# Pre-hashed admin password (generated during deployment)
ADMIN_CREDENTIALS = {
    "username": os.getenv('ADMIN_USER'),
    "password": os.getenv('ADMIN_PASSWORD')
}

# Route for user login to get a JWT token
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    if not username or not password:
        return jsonify({"message": "Missing username or password"}), 400

    # Validate user credentials
    admin_pass = generate_password_hash(ADMIN_CREDENTIALS["password"])
    if username == ADMIN_CREDENTIALS["username"] and check_password_hash(admin_pass, password):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200

    return jsonify({"message": "Invalid credentials"}), 401

# Protected endpoint: woodxel_chatbot
@app.route('/woodxel_chatbot', methods=['POST'])
@jwt_required()
def woodxel_chatbot():
    data = request.get_json()
    print(data)
    if not data or 'input' not in data or 'history' not in data or 'user_name' not in data:
        return jsonify({"message": "Missing required fields"}), 400
    try:
        chat = WoodxelChatbot(user_name=data['user_name'])
        result = chat.chat_with_history(data['input'], data['history'])
        return jsonify({"response": result}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

# Protected endpoint: lignum_chatbot
@app.route('/lignum_chatbot', methods=['POST'])
@jwt_required()
def lignum_chatbot():
    data = request.get_json()
    print(data)
    if not data or 'input' not in data or 'history' not in data or 'user_name' not in data:
        return jsonify({"message": "Missing required fields"}), 400
    try:
        print('before chat')
        chat = LignumChatbot(user_name=data['user_name'])
        print('chat')
        result = chat.chat_with_history(data['input'], data['history'])
        return jsonify({"response": result}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


# Protected endpoint: summarize_conversation
@app.route('/summarize_conversation', methods=['POST'])
@jwt_required()
def summarize_conversation():
    data = request.get_json()
    print(data)
    if not data or 'history' not in data:
        return jsonify({"message": "Missing required fields: 'history'"}), 400
    try:
        chat = LLM()
        result = chat.run(data['history'])
        return jsonify({"response": result}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
