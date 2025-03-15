import os
import telebot
from openai import OpenAI
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import get_company_db, ChatHistory, Inquiry
from chatbot import get_chatbot_response
from config import get_company_settings

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatInput(BaseModel):
    message: str


class InquiryInput(BaseModel):
    contact: str
    inquiry: str


def send_telegram_notification(chat_id, message, bot_token):
    try:
        telegram_bot = telebot.TeleBot(bot_token)
        telegram_bot.send_message(chat_id, message)
    except Exception as e:
        print(f"텔레그램 알림 실패: {e}")


app = FastAPI()


@app.post("/chat/{company_name}")
def chat_endpoint(company_name: str, chat_input: ChatInput):
    settings = get_company_settings(company_name)

    user_message = chat_input.message

    if any(x in user_message for x in ["그림", "이미지", "그려", "생성"]):
        client = OpenAI(api_key=settings["OPENAI_API_KEY"])
        response = client.images.generate(
            model="dall-e-3", prompt=user_message, size="1024x1024", n=1
        )
        bot_response = response.data[0].url
    else:
        bot_response = get_chatbot_response(user_message, company_name)

    Session = get_company_db(settings["DB_PATH"])
    with Session() as session:
        chat = ChatHistory(user_message=chat_input.message, bot_response=bot_response)
        session.add(chat)
        session.commit()

    send_telegram_notification(
        settings["TELEGRAM_CHAT_ID"],
        f"📌 [{company_name}] 챗봇 기록\n👤 질문: {chat_input.message}\n🤖 답변: {bot_response}",
    )

    return {"response": bot_response}


@app.post("/submit-inquiry/{company_name}")
def submit_inquiry(company_name: str, inquiry: InquiryInput):
    Session = get_company_db(get_company_settings(company_name)["DB_PATH"])
    with Session() as session:
        new_inquiry = Inquiry(contact=inquiry.contact, inquiry=inquiry.inquiry)
        session.add(new_inquiry)
        session.commit()

    return {"message": f"{company_name}의 문의가 저장되었습니다."}


@app.get("/history/{company_name}")
def get_chat_history(company_name: str, limit: int = 5):
    Session = get_company_db(get_company_settings(company_name)["DB_PATH"])
    with Session() as session:
        history = (
            session.query(ChatHistory)
            .order_by(ChatHistory.timestamp.desc())
            .limit(limit)
            .all()
        )

    return {
        "history": [
            {"user_message": h.user_message, "bot_response": h.bot_response, "timestamp": h.timestamp}
            for h in history
        ]
    }


@app.get("/inquiries/{company_name}")
def get_inquiries(company_name: str):
    Session = get_company_db(get_company_settings(company_name)["DB_PATH"])
    with Session() as session:
        inquiries = session.query(Inquiry).order_by(Inquiry.timestamp.desc()).all()

    return [
        {"contact": i.contact, "inquiry": i.inquiry, "timestamp": i.timestamp}
        for i in inquiries
    ]


@app.post("/update-vector-db/{company_name}")
def update_vector_db(company_name: str):
    try:
        create_vector_db(company_name)
        return {"message": f"{company_name} 벡터DB 업데이트 완료."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))