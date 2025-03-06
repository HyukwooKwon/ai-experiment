import os
from dotenv import load_dotenv

# ✅ .env 파일 로드
load_dotenv()

# ✅ API 키 가져오기
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY가 설정되지 않았습니다! .env 파일 확인 필요")
