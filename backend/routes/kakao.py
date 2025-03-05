from flask import Blueprint, request, jsonify
from chatbot import get_chatbot_response
from config import KAKAO_REST_API_KEY

kakao_bp = Blueprint("kakao", __name__)

@kakao_bp.route("/chat/kakao", methods=["GET", "POST"])
def kakao_chat():
    if request.method == "GET":
        return jsonify({"message": "카카오 API는 POST 요청만 허용합니다."})

    try:
        data = request.json
        print("카카오 요청 데이터:", data)  # ← JSON 데이터 출력
        
        user_message = data.get("userRequest", {}).get("utterance", "")

        bot_reply = get_chatbot_response(user_message)

        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [{"simpleText": {"text": bot_reply}}]
            }
        })
    except Exception as e:
        return jsonify({"error": "서버 오류 발생"}), 500

