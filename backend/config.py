import os
from dotenv import load_dotenv

# ✅ 환경변수 로드
load_dotenv()

# ✅ 업체별 환경변수 동적으로 설정
COMPANY_NAME = os.getenv("COMPANY_NAME")

if not COMPANY_NAME:
    raise ValueError("❌ 환경 변수 'COMPANY_NAME'이 설정되지 않았습니다. Render 환경변수를 확인하세요!")

# ✅ 업체별 OpenAI API 키 가져오기
OPENAI_API_KEY = os.getenv(f"OPENAI_API_KEY_{COMPANY_NAME}")

if not OPENAI_API_KEY:
    raise ValueError(f"❌ {COMPANY_NAME}의 OpenAI API 키가 설정되지 않았습니다. Render 환경변수를 확인하세요!")
