import os
from dotenv import load_dotenv

# ✅ 환경변수 로드
load_dotenv()

# ✅ 기본 환경변수 설정
COMPANY_NAME = os.getenv("COMPANY_NAME")

if not COMPANY_NAME:
    raise ValueError("❌ 환경 변수 'COMPANY_NAME'이 설정되지 않았습니다.")

# ✅ 업체별 OpenAI API 키 가져오기
AI_MODEL = os.getenv(f"AI_MODEL_{COMPANY_NAME}", "gpt-3.5-turbo")
OPENAI_API_KEY = os.getenv(f"OPENAI_API_KEY_{COMPANY_NAME}")  # 변경됨!


# ✅ 디버깅을 위해 환경 변수 출력 (테스트 후 삭제 가능)
print(f"🔍 COMPANY_NAME: {COMPANY_NAME}")
print(f"🔍 AI_MODEL: {AI_MODEL}")
print(f"🔍 OPENAI_API_KEY: {'설정됨' if OPENAI_API_KEY else '설정되지 않음'}")

if not OPENAI_API_KEY:
    raise ValueError(f"❌ {COMPANY_NAME}의 OpenAI API 키가 설정되지 않았습니다.")

# ✅ 백엔드 URL 설정 (로컬 or 서버 환경 자동 감지)
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# ✅ 업체별 AI 모델 가져오기
AI_MODEL = os.getenv(f"AI_MODEL_{COMPANY_NAME}", "gpt-3.5-turbo")
