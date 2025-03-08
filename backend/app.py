import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from chatbot import get_chatbot_response  # ✅ AI 응답 함수 가져오기
from chatbot import create_or_update_faiss  # 🔹 벡터DB 업데이트 함수 추가

# ✅ Flask 앱 생성
app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)  # 모든 요청 허용

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")  # ✅ Render에서도 HTML 제공

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "잘못된 요청 형식입니다. JSON 데이터 확인 필요"}), 400

        user_message = data["message"]
        bot_response = get_chatbot_response(user_message)

        return jsonify({"reply": bot_response})

    except Exception as e:
        return jsonify({"error": f"서버 오류 발생: {str(e)}"}), 500
    
def update_db():
    try:
        create_or_update_faiss()
        return jsonify({"message": "✅ 벡터DB가 성공적으로 업데이트되었습니다!"}), 200
    except Exception as e:
        return jsonify({"error": f"❌ 업데이트 실패: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
