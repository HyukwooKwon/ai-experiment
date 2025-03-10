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
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "잘못된 요청 형식입니다."}), 400

        user_message = data["message"]
        bot_response = get_chatbot_response(user_message, company_name)

        Session, ChatHistory = get_company_db(company_name)
        session = Session()

        chat_entry = ChatHistory(user_message=user_message, bot_response=bot_response)
        session.add(chat_entry)
        session.commit()

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

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
