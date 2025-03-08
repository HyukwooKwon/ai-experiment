import os
import telebot
import requests
from dotenv import load_dotenv  # ✅ .env 파일 로드

# ✅ .env 파일 로드
load_dotenv()

# ✅ Telegram 봇 토큰 설정 (.env에서 불러오기)
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN이 설정되지 않았습니다! .env 파일을 확인하세요.")

bot = telebot.TeleBot(BOT_TOKEN)

# ✅ Flask 백엔드 URL (Render에 배포된 API 주소 입력)
BACKEND_URL = "https://chatbot-back-fegf.onrender.com/chat"

# ✅ 메시지 처리 함수
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_text = message.text  # 사용자 입력
    chat_id = message.chat.id

    # ✅ 백엔드에 사용자 메시지 전송
    try:
        response = requests.post(BACKEND_URL, json={"message": user_text})
        bot_response = response.json().get("reply", "❌ 오류: 응답을 받을 수 없습니다.")
    except Exception as e:
        bot_response = f"❌ 서버 오류 발생: {str(e)}"

    # ✅ 텔레그램으로 응답 전송
    bot.send_message(chat_id, bot_response)

# ✅ 봇 실행
print("🚀 텔레그램 봇 실행 중...")
bot.polling()
