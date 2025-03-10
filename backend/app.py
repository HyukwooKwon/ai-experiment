# ✅ app.py (멀티테넌트로 수정된 최종본)

import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from chatbot import get_chatbot_response
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# ✅ 현재 실행 중인 서버의 업체명
CURRENT_COMPANY = os.getenv("COMPANY_NAME")

if not CURRENT_COMPANY:
    raise ValueError("❌ 환경 변수 'COMPANY_NAME'이 설정되지 않았습니다. Render 환경변수를 확인하세요!")

# ✅ AI 키 확인
OPENAI_API_KEY = os.getenv(f"OPENAI_API_KEY_{CURRENT_COMPANY}")
if not OPENAI_API_KEY:
    raise ValueError(f"❌ {CURRENT_COMPANY}의 OpenAI API 키가 설정되지 않았습니다. Render 환경변수를 확인하세요!")

print(f"🚀 서버 시작됨 - 업체: {CURRENT_COMPANY}, 포트: {os.getenv('PORT')}")

# 동적 DB 연결 함수
def get_company_db(company_name):
    db_path = f'databases/{company_name}.db'
    engine = create_engine(f'sqlite:///{db_path}', echo=False)
    Base = declarative_base()

    class ChatHistory(Base):
        __tablename__ = 'chat_history'
        id = Column(Integer, primary_key=True)
        user_message = Column(String)
        bot_response = Column(String)
        timestamp = Column(DateTime, default=datetime.now)

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    return Session, ChatHistory

@app.route("/chatbot/<company_name>", methods=["POST"])
def chatbot(company_name):
    try:
        if company_name != CURRENT_COMPANY:
            return jsonify({"error": f"❌ 현재 서버는 {CURRENT_COMPANY} 전용입니다. {company_name} 요청을 받을 수 없습니다."}), 403

        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "잘못된 요청 형식입니다."}), 400

        user_message = data["message"]

        # ✅ 업체별 AI 모델 및 API 키 가져오기
        ai_model = os.getenv(f"AI_MODEL_{company_name}", "gpt-3.5-turbo")
        openai_api_key = os.getenv(f"OPENAI_API_KEY_{company_name}")

        if not openai_api_key:
            return jsonify({"error": "해당 업체의 API 키가 설정되지 않았습니다."}), 500

        bot_response = get_chatbot_response(user_message, company_name, ai_model, openai_api_key)

        return jsonify({"reply": bot_response})

    except Exception as e:
        return jsonify({"error": f"서버 오류 발생: {str(e)}"}), 500


@app.route("/update-db/<company_name>", methods=["POST"])
def update_db(company_name):
    try:
        create_or_update_faiss(company_name)
        return jsonify({"message": f"✅ {company_name} 벡터DB가 성공적으로 업데이트되었습니다!"}), 200
    except Exception as e:
        return jsonify({"error": f"❌ 업데이트 실패: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # 환경변수에서 포트 가져오기
    app.run(host="0.0.0.0", port=port)
