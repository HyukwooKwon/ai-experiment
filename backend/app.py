import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from chatbot import get_chatbot_response

# ✅ Flask 앱 생성
app = Flask(__name__)
CORS(app)  # 모든 요청 허용

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "AI Chatbot Backend is Running!"})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "메시지가 비어있습니다."}), 400

    bot_response = get_chatbot_response(user_message)
    return jsonify({"reply": bot_response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
