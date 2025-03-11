import sqlite3
import datetime
from pathlib import Path

# 데이터베이스 경로 설정
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "chat_history.db"

def create_table():
    """ 채팅 기록 저장 테이블 생성 """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_chat(user_message, bot_response):
    """ 사용자의 질문과 챗봇 응답 저장 """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO chat_history (user_message, bot_response, timestamp) VALUES (?, ?, ?)",
                   (user_message, bot_response, timestamp))
    conn.commit()
    conn.close()

def get_recent_chats(limit=10):
    """ 최근 대화 기록 조회 (기본 10개) """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chat_history ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def search_chat(keyword):
    """ 특정 키워드가 포함된 대화 검색 """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chat_history WHERE user_message LIKE ?", ('%' + keyword + '%',))
    results = cursor.fetchall()
    conn.close()
    return results

def delete_old_chats(days=90):
    """ 30일 이상 지난 데이터 삭제 """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_history WHERE timestamp < datetime('now', '-{} days')".format(days))
    conn.commit()
    conn.close()

# 처음 실행할 때 테이블 생성
create_table()
