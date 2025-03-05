import logging
from flask import Blueprint, request, jsonify
from chatbot import get_chatbot_response

chat_bp = Blueprint("chat", __name__)
logger = logging.getLogger(__name__)

@chat_bp.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        user_message = data.get("message", "")

        logger.info(f"📩 [Web] 요청 받음: {user_message}")  # ✅ 로그 추가

        bot_reply = get_chatbot_response(user_message)

        logger.info(f"🤖 [Web] 챗봇 응답: {bot_reply}")  # ✅ 로그 추가
        return jsonify({"reply": bot_reply})

    except Exception as e:
        logger.error(f"❌ [Web] 오류 발생: {str(e)}")
        return jsonify({"error": f"서버 오류 발생: {str(e)}"}), 500
