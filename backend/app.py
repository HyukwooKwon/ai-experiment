import os
import telebot
from openai import OpenAI
from fastapi import FastAPI, HTTPException, Request  # ✅ 정확한 import
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

    telegram_upload_bot_token = settings["TELEGRAM_BOT_TOKEN_UPLOAD"]
    telegram_chat_id = settings["TELEGRAM_CHAT_ID"]

    user_message = chat.message.strip()

    image_keywords = ["그림", "이미지", "그려", "생성"]
    if any(keyword in user_message for keyword in image_keywords):
        prompt = user_message
        try:
            client = OpenAI(api_key=openai_api_key)
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                n=1
            )
            image_url = response.data[0].url
            bot_response = f"이미지를 생성했습니다: {image_url}"
        except Exception as e:
            bot_response = f"이미지 생성 실패: {str(e)}"
    else:
        bot_response = get_chatbot_response(user_message, company_name, ai_model, openai_api_key)

    Session, ChatHistory, _ = get_company_db(company_name)
    session = Session()
    new_chat = ChatHistory(user_message=user_message, bot_response=bot_response)
    session.add(new_chat)
    session.commit()
    session.close()

    try:
        telegram_bot_upload = telebot.TeleBot(telegram_upload_bot_token)
        telegram_bot_upload.send_message(
            telegram_chat_id,
            f"📌 [업체: {company_name}의 새로운 챗봇 기록]\n\n👤질문:\n{user_message}\n\n🤖답변:\n{bot_response}"
        )
    except Exception as e:
        print(f"⚠️ 텔레그램 메시지 전송 실패: {str(e)}")

    return {"reply": bot_response}

# ✅ 카카오톡 연동을 위한 별도 API 추가 (중요)
@app.post("/chatbot/{company_name}/kakao")
async def kakao_chatbot(company_name: str, request: Request):
    body = await request.json()
    user_message = body["userRequest"]["utterance"].strip()

    try:
        settings = get_company_settings(company_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    openai_api_key = settings["OPENAI_API_KEY"]
    ai_model = "gpt-3.5-turbo"  # 카카오톡 전용으로 더 빠른 모델 사용하기!

    bot_response = get_chatbot_response(user_message, company_name, ai_model, openai_api_key)

    return {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": bot_response
                    }
                }
            ]
        }
    }


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
