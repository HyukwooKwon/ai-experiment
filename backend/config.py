import os
from dotenv import load_dotenv

# ✅ 환경변수 로드
load_dotenv()

# ✅ 지원하는 업체 리스트 가져오기
COMPANY_NAMES = os.getenv("COMPANY_NAMES", "").split(",")

def get_company_settings(company_name):
    """ 특정 업체의 AI 모델과 API 키, 텔레그램 봇 토큰을 가져옴 """
    if company_name not in COMPANY_NAMES:
        raise ValueError(f"❌ '{company_name}'는 이 서버에서 지원되지 않는 업체입니다.")

    ai_model = os.getenv("AI_MODEL")  # Render에서 공통으로 적용된 모델 사용
    openai_api_key = os.getenv("OPENAI_API_KEY")  # 모델별 API 키
    telegram_bot_token = os.getenv(f"TELEGRAM_BOT_TOKEN_{company_name}")  # 업체별 텔레그램 봇 토큰

    if not ai_model or not openai_api_key:
        raise ValueError(f"❌ '{ai_model}'의 OpenAI API 키가 설정되지 않았습니다.")

    if not telegram_bot_token:
        raise ValueError(f"❌ '{company_name}'의 텔레그램 봇 토큰이 설정되지 않았습니다.")

    return {
        "AI_MODEL": ai_model,
        "OPENAI_API_KEY": openai_api_key,
        "TELEGRAM_BOT_TOKEN": telegram_bot_token
    }


# ✅ 백엔드 URL 설정 (로컬 or 서버 환경 자동 감지)
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")