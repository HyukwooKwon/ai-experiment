import os
import telebot
import requests
from dotenv import load_dotenv

# ✅ 환경변수 로드
load_dotenv()

COMPANY_NAME = os.getenv("COMPANY_NAME", "defaultCompany")
BOT_TOKEN = os.getenv(f"TELEGRAM_BOT_TOKEN_{COMPANY_NAME}")

if not BOT_TOKEN:
    raise ValueError(f"❌ {COMPANY_NAME}의 TELEGRAM_BOT_TOKEN이 설정되지 않았습니다!")

# ✅ 백엔드 URL 설정 (로컬 또는 서버 환경 자동 감지)
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000") + f"/chatbot/{COMPANY_NAME}"

bot = telebot.TeleBot(BOT_TOKEN)

# ✅ 봇의 사용자 정보 가져오기
bot_info = bot.get_me()
BOT_USERNAME = bot_info.username
BOT_NICKNAMES = [f"@{BOT_USERNAME}", "@AI봇", "@챗봇"]

# ✅ 태그된 메시지 또는 답장된 메시지에만 반응하도록 설정
@bot.message_handler(func=lambda message: (
    (message.text and any(tag in message.text for tag in BOT_NICKNAMES)) or 
    (message.reply_to_message and message.reply_to_message.from_user.id == bot_info.id)
))
def handle_message(message):
    user_text = message.text or ""
    for tag in BOT_NICKNAMES:
        user_text = user_text.replace(tag, "").strip()

    chat_id = message.chat.id

    try:
        response = requests.post(BACKEND_URL, json={"message": user_text}, timeout=5)
        if response.status_code == 200:
            bot_response = response.json().get("reply", "❌ 응답을 받을 수 없습니다.")
        else:
            bot_response = f"❌ 서버 오류 발생 (상태 코드: {response.status_code})"
    except requests.exceptions.RequestException as e:
        bot_response = f"❌ 서버 연결 오류 발생: {str(e)}"

    bot.send_message(chat_id, bot_response)

# ✅ 텔레그램 봇 실행 (예외 발생 시 자동 재시작)
while True:
    try:
        print(f"🚀 {COMPANY_NAME} 텔레그램 봇 실행 중... (토큰: {BOT_TOKEN})")
        bot.polling()
    except Exception as e:
        print(f"⚠️ 봇 오류 발생: {str(e)}. 5초 후 재시작...")
        import time
        time.sleep(5)
