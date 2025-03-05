from flask import Blueprint, request, jsonify
from chatbot import get_chatbot_response
import logging

naver_bp = Blueprint("naver", __name__)
logger = logging.getLogger(__name__)

@naver_bp.route("/chat/naver", methods=["POST"])
def naver_talktalk():
    try:
        # 네이버에서 받은 요청 데이터를 JSON으로 받기
        data = request.json
        logger.info(f"🔹 네이버 톡톡 Webhook 요청 도착! 데이터: {data}")

        # 네이버에서 보낸 메시지 추출
        user_message = data.get("text", "")

        # 메시지가 없으면 기본 메시지 반환
        if not user_message:
            return jsonify({"event": "send", "text": "메시지를 입력해주세요."})

        # 챗봇 응답 생성
        bot_reply = get_chatbot_response(user_message)
        logger.info(f"✅ 챗봇 응답: {bot_reply}")

        # 네이버 톡톡 Webhook 응답 형식
        return jsonify({
            "event": "send",
            "text": bot_reply
        })

    except Exception as e:
        logger.error(f"❌ 네이버 톡톡 Webhook 오류: {str(e)}")
        return jsonify({"error": "서버 오류 발생"}), 500
