import requests
from flask import Blueprint, request, jsonify
from chatbot import get_chatbot_response
from config import TELEGRAM_BOT_TOKEN

telegram_bp = Blueprint("telegram", __name__)

@telegram_bp.route("/chat/telegram", methods=["POST"])
def telegram():
    try:
        data = request.json
        user_message = data.get("message", {}).get("text", "")

        if not user_message:
            return jsonify({"error": "Invalid request"}), 400

        bot_reply = get_chatbot_response(user_message)

        # 텔레그램 메시지 전송
        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": data["message"]["chat"]["id"],
            "text": bot_reply
        }
        requests.post(telegram_url, json=payload)

        return jsonify({"status": "ok"})

    except Exception as e:
        return jsonify({"error": "서버 오류 발생"}), 500
