import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())  # .env 파일 로드

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

print("OpenAI API Key:", os.getenv("OPENAI_API_KEY"))
print("Kakao REST API Key:", os.getenv("KAKAO_REST_API_KEY"))

# ✅ .env 파일 강제 로드
dotenv_path = find_dotenv()
if dotenv_path:
    load_dotenv(dotenv_path)
else:
    print("⚠️ .env 파일을 찾을 수 없습니다!")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY must be set in .env file")
