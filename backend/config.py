import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

COMPANY_AI_MODELS = {
    "companyA": os.getenv("AI_MODEL_companyA", "gpt-4-turbo"),
    "companyB": os.getenv("AI_MODEL_companyB", "gpt-3.5-turbo"),
    "companyC": os.getenv("AI_MODEL_companyC", "gpt-4-turbo"),
    "companyD": os.getenv("AI_MODEL_companyD", "gpt-3.5-turbo"),
}

API_KEYS = {
    "gpt-4-turbo": os.getenv("OPENAI_API_KEY_gpt-4-turbo"),
    "gpt-3.5-turbo": os.getenv("OPENAI_API_KEY_gpt-3.5-turbo"),
}

ALLOWED_COMPANIES = list(COMPANY_AI_MODELS.keys())

def get_company_settings(company_name):
    if company_name not in ALLOWED_COMPANIES:
        raise ValueError(f"❌ 지원되지 않는 업체입니다: {company_name}")

    ai_model = COMPANY_AI_MODELS.get(company_name)
    openai_api_key = API_KEYS.get(ai_model)

    # ✅ 챗봇 응답용으로는 모델별로 구분된 봇 토큰 사용
    telegram_bot_token = os.getenv(f"TELEGRAM_BOT_TOKEN_{ai_model}")

    # ✅ 기록 업로드용으로는 공통 통합봇토큰 사용
    telegram_upload_bot_token = os.getenv("TELEGRAM_BOT_TOKEN_UPLOAD")
    telegram_chat_id = os.getenv(f"TELEGRAM_CHAT_ID_{company_name}")

    if not all([ai_model, openai_api_key, telegram_bot_token, telegram_upload_bot_token, telegram_chat_id]):
        raise ValueError(f"❌ {company_name} 설정이 누락됨: 환경변수를 확인하세요.")

    return {
        "AI_MODEL": ai_model,
        "OPENAI_API_KEY": openai_api_key,
        "TELEGRAM_BOT_TOKEN": telegram_bot_token, # 모델별 봇토큰 (응답용)
        "TELEGRAM_BOT_TOKEN_UPLOAD": telegram_upload_bot_token, # 업로드용 공통 봇 토큰
        "TELEGRAM_CHAT_ID": telegram_chat_id
    }

# ✅ 백엔드 URL 설정
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
print(f"🔍 백엔드 URL: {BACKEND_URL}")
