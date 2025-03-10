import os
import telebot
import requests
from dotenv import load_dotenv

# ✅ 환경변수 로드
load_dotenv()

# ✅ 업체별 환경변수 설정
COMPANY_NAME = os.getenv("COMPANY_NAME")
BOT_TOKEN = os.getenv(f"TELEGRAM_BOT_TOKEN_{COMPANY_NAME}")  # ✅ 업체별 봇 토큰 가져오기

if not BOT_TOKEN or not COMPANY_NAME:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN 또는 COMPANY_NAME이 설정되지 않았습니다!")

BACKEND_URL = f"https://backend.onrender.com/chatbot/{COMPANY_NAME}"

bot = telebot.TeleBot(BOT_TOKEN)

# ✅ 봇의 사용자 정보 가져오기
bot_info = bot.get_me()
BOT_USERNAME = bot_info.username  # 예: "my_ai_bot"
BOT_NICKNAMES = [f"@{BOT_USERNAME}", "@AI봇", "@챗봇"]  # ✅ 한글 태그 포함 가능

# ✅ 태그된 메시지 또는 답장된 메시지에 반응하도록 설정
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
        response = requests.post(BACKEND_URL, json={"message": user_text})
        bot_response = response.json().get("reply", "❌ 응답을 받을 수 없습니다.")
    except Exception as e:
        bot_response = f"❌ 서버 오류 발생: {str(e)}"

    bot.send_message(chat_id, bot_response)

# ✅ 텔레그램 봇 실행
print(f"🚀 텔레그램 봇 실행 중... (업체: {COMPANY_NAME})")
bot.polling()