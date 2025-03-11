import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
from chatbot import get_chatbot_response
from create_vector_db import create_or_update_faiss
from config import get_company_settings  # ✅ 동적 환경 변수 불러오기

# ✅ 모든 업체의 설정을 테스트 출력
for company in ["companyA", "companyB", "companyC", "companyD"]:
    settings = get_company_settings(company)
    print(f"{company} - AI_MODEL: {settings['AI_MODEL']}, OPENAI_API_KEY: {settings['OPENAI_API_KEY'][:5]}*****")

# ✅ FastAPI 앱 초기화
app = FastAPI()

# ✅ CORS 설정 추가 (모든 출처 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ SQLite 데이터베이스 설정
Base = declarative_base()

def get_company_db(company_name):
    """ 업체별 SQLite 데이터베이스를 설정 """
    db_path = f"databases/{company_name}.db"
    engine = create_engine(f"sqlite:///{db_path}", echo=False)

    # ✅ SQLite 데이터베이스 설정
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
    """ 업체별 SQLite 데이터베이스를 설정 """
    db_path = f"databases/{company_name}.db"
    engine = create_engine(f"sqlite:///{db_path}", echo=False)

    # ✅ 기존 테이블을 재사용하도록 변경
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    
    return Session, ChatHistory, Inquiry


# ✅ 데이터 모델 정의
class ChatInput(BaseModel):
    message: str

class InquiryInput(BaseModel):
    contact: str
    inquiry: str

# ✅ AI 챗봇 응답 API (업체별 설정 동적 적용)
@app.post("/chatbot/{company_name}")
def chatbot(company_name: str, chat: ChatInput):
    """ 사용자의 질문을 받아 챗봇 응답을 반환하고 기록 저장 """
    try:
        settings = get_company_settings(company_name)  # ✅ 요청마다 업체별 환경 변수 적용
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    ai_model = settings["AI_MODEL"]
    openai_api_key = settings["OPENAI_API_KEY"]
    
    # ✅ 디버깅 출력
    print(f"📌 {company_name} - AI_MODEL={ai_model}, API_KEY={openai_api_key[:5]}*****")
    
    # ✅ API 키 확인 (없으면 에러)
    if not openai_api_key:
        raise HTTPException(status_code=400, detail=f"❌ {company_name}의 OpenAI API 키가 설정되지 않았습니다!")

    # ✅ 챗봇 응답 생성
    bot_response = get_chatbot_response(chat.message, company_name, ai_model, openai_api_key)

    # ✅ 대화 기록 저장
    Session, ChatHistory, _ = get_company_db(company_name)
    session = Session()
    new_chat = ChatHistory(user_message=chat.message, bot_response=bot_response)
    session.add(new_chat)
    session.commit()
    session.close()

    return {"reply": f"{company_name}의 챗봇 응답: {bot_response}"}

# ✅ 최근 대화 조회 API
@app.get("/chatbot/history/{company_name}")
def get_chat_history(company_name: str, limit: int = 10):
    """ 최근 대화 기록 조회 """
    Session, ChatHistory, _ = get_company_db(company_name)
    session = Session()

    history = session.query(ChatHistory).order_by(ChatHistory.timestamp.desc()).limit(limit).all()
    session.close()

    return {"history": [{"message": h.user_message, "reply": h.bot_response, "timestamp": h.timestamp} for h in history]}

# ✅ 문의 제출 API
@app.post("/submit-inquiry/{company_name}")
def submit_inquiry(company_name: str, inquiry: InquiryInput):
    """ 특정 업체의 문의 내용을 저장하는 API """
    Session, _, Inquiry = get_company_db(company_name)
    session = Session()

    try:
        new_inquiry = Inquiry(contact=inquiry.contact, inquiry=inquiry.inquiry)
        session.add(new_inquiry)
        session.commit()
        session.close()
        return {"message": f"✅ {company_name}의 문의가 성공적으로 저장되었습니다!"}
    except Exception as e:
        session.rollback()
        session.close()
        raise HTTPException(status_code=500, detail=f"❌ {company_name}의 문의 저장 실패: {str(e)}")

# ✅ 문의 목록 조회 API
@app.get("/inquiries/{company_name}")
def get_inquiries(company_name: str):
    """ 특정 업체의 저장된 문의 목록을 반환하는 API """
    Session, _, Inquiry = get_company_db(company_name)
    session = Session()

    inquiries = session.query(Inquiry).order_by(Inquiry.timestamp.desc()).all()
    session.close()

    return [{"contact": i.contact, "inquiry": i.inquiry, "timestamp": i.timestamp} for i in inquiries]

# ✅ 벡터 DB 업데이트 API
@app.post("/update-db/{company_name}")
def update_db(company_name: str):
    """ 특정 업체의 벡터 DB 업데이트 """
    try:
        create_or_update_faiss(company_name)
        return {"message": f"✅ {company_name}의 벡터DB가 성공적으로 업데이트되었습니다!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ {company_name}의 업데이트 실패: {str(e)}")

# ✅ 서버 실행
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 5000))  # 환경변수에서 포트 가져오기
    uvicorn.run(app, host="0.0.0.0", port=port)
