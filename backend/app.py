import os
import telebot
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
from chatbot import get_chatbot_response
from create_vector_db import create_or_update_faiss
from config import get_company_settings

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base = declarative_base()

class ChatHistory(Base):
    __tablename__ = "chat_history"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_message = Column(String, nullable=False)
    bot_response = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)

class Inquiry(Base):
    __tablename__ = "inquiries"
    id = Column(Integer, primary_key=True, autoincrement=True)
    contact = Column(String, nullable=False)
    inquiry = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)

def get_company_db(company_name):
    db_path = f"databases/{company_name}.db"
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session, ChatHistory, Inquiry

class ChatInput(BaseModel):
    message: str

class InquiryInput(BaseModel):
    contact: str
    inquiry: str

@app.post("/chatbot/{company_name}")
def chatbot(company_name: str, chat: ChatInput):
    try:
        settings = get_company_settings(company_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    ai_model = settings["AI_MODEL"]
    openai_api_key = settings["OPENAI_API_KEY"]

    # ✅ 모델별 텔레그램 봇 토큰 (사용자와의 챗봇 응답)
    telegram_bot_token = settings["TELEGRAM_BOT_TOKEN"]
    # ✅ 통합 업로드 봇토큰 및 업체별 채널 ID (기록 업로드)
    telegram_upload_bot_token = settings["TELEGRAM_BOT_TOKEN_UPLOAD"]
    telegram_chat_id = settings["TELEGRAM_CHAT_ID"]

    bot_response = get_chatbot_response(chat.message, company_name, ai_model, openai_api_key)

    # DB 저장
    Session, ChatHistory, _ = get_company_db(company_name)
    session = Session()
    new_chat = ChatHistory(user_message=chat.message, bot_response=bot_response)
    session.add(new_chat)
    session.commit()
    session.close()

    # ✅ 챗봇기록 텔레그램 채널로 업로드 (업로드용 통합봇 사용)
    try:
        telegram_bot_upload = telebot.TeleBot(telegram_upload_bot_token)
        telegram_bot_upload.send_message(
            telegram_chat_id,
            f"📌 [업체: {company_name}의 새로운 챗봇 기록]\n\n👤질문:\n{chat.message}\n\n🤖답변:\n{bot_response}"
        )
    except Exception as e:
        print(f"⚠️ 텔레그램 메시지 전송 실패: {str(e)}")

    return {"reply": f"{company_name}의 챗봇 응답: {bot_response}"}

# 나머지 API는 기존 코드 그대로 유지 (수정 X)
@app.get("/chatbot/history/{company_name}")
def get_chat_history(company_name: str, limit: int = 10):
    Session, ChatHistory, _ = get_company_db(company_name)
    session = Session()
    history = session.query(ChatHistory).order_by(ChatHistory.timestamp.desc()).limit(limit).all()
    session.close()
    return {"history": [{"message": h.user_message, "reply": h.bot_response, "timestamp": h.timestamp} for h in history]}

@app.post("/submit-inquiry/{company_name}")
def submit_inquiry(company_name: str, inquiry: InquiryInput):
    Session, _, Inquiry = get_company_db(company_name)
    session = Session()
    new_inquiry = Inquiry(contact=inquiry.contact, inquiry=inquiry.inquiry)
    session.add(new_inquiry)
    session.commit()
    session.close()
    return {"message": f"✅ {company_name}의 문의가 성공적으로 저장되었습니다!"}

@app.get("/inquiries/{company_name}")
def get_inquiries(company_name: str):
    Session, _, Inquiry = get_company_db(company_name)
    session = Session()
    inquiries = session.query(Inquiry).order_by(Inquiry.timestamp.desc()).all()
    session.close()
    return [{"contact": i.contact, "inquiry": i.inquiry, "timestamp": i.timestamp} for i in inquiries]

@app.post("/update-db/{company_name}")
def update_db(company_name: str):
    try:
        create_or_update_faiss(company_name)
        return {"message": f"✅ {company_name}의 벡터DB가 성공적으로 업데이트되었습니다!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ {company_name}의 업데이트 실패: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port)
