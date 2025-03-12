import os
import telebot
import requests
from dotenv import load_dotenv
from config import COMPANY_AI_MODELS

# ✅ 환경변수 로드
load_dotenv()

COMPANY_NAME = os.getenv("COMPANY_NAME", "defaultCompany")
AI_MODEL = COMPANY_AI_MODELS.get(COMPANY_NAME)

if not AI_MODEL:
    raise ValueError(f"❌ {COMPANY_NAME}의 AI 모델 설정이 없습니다!")

# 모델별 봇 토큰 사용
BOT_TOKEN = os.getenv(f"TELEGRAM_BOT_TOKEN_{AI_MODEL}")

if not BOT_TOKEN:
    raise ValueError(f"❌ {COMPANY_NAME}({AI_MODEL})의 TELEGRAM_BOT_TOKEN이 설정되지 않았습니다!")

# ✅ 백엔드 URL 설정 (로컬 또는 서버 환경 자동 감지)
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000") + f"/chatbot/{COMPANY_NAME}"

bot = telebot.TeleBot(BOT_TOKEN)

# ✅ 봇 정보 가져오기
bot_info = bot.get_me()
BOT_USERNAME = bot_info.username
BOT_NICKNAMES = [f"@{BOT_USERNAME}", "@AI봇", "@챗봇"]

# ✅ 메시지 핸들러 (태그 또는 답장만 응답)
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
        response.raise_for_status()
        bot_response = response.json().get("reply", "❌ 응답을 받을 수 없습니다.")
    except requests.exceptions.HTTPError as e:
        bot_response = f"❌ 서버 오류 발생 (상태 코드: {response.status_code})"
    except requests.exceptions.RequestException as e:
        bot_response = f"❌ 서버 연결 오류 발생: {str(e)}"

    bot.send_message(chat_id, bot_response)

# ✅ 텔레그램 봇 실행 (예외 발생 시 자동 재시작)
while True:
    try:
        print(f"🚀 {COMPANY_NAME}({AI_MODEL}) 텔레그램 봇 실행 중...")
        bot.polling()
    except Exception as e:
        print(f"⚠️ 봇 오류 발생: {str(e)}. 5초 후 재시작...")
        import time
        time.sleep(5)