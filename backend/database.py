# database.py (신규 생성)
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

Base = declarative_base()

class ChatHistory(Base):
    __tablename__ = "chat_history"
    id = Column(Integer, primary_key=True)
    user_message = Column(String, nullable=False)
    bot_response = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)

class Inquiry(Base):
    __tablename__ = "inquiries"
    id = Column(Integer, primary_key=True)
    contact = Column(String, nullable=False)
    inquiry = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)

def get_company_db(db_path):
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)
