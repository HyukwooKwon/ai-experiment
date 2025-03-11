import os
from dotenv import load_dotenv

# ✅ 환경 변수 강제 로드 (.env 파일이 자동 적용되지 않을 수도 있음)
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

# ✅ 배포 환경 감지 (한 서버에서 GPT-4 & GPT-3.5를 모두 지원)
DEPLOY_ENV = os.getenv("DEPLOY_ENV", "both")  # 기본값은 한 서버에서 모든 모델 지원
print(f"🔍 현재 배포 환경: {DEPLOY_ENV}")

# ✅ 업체별 AI 모델 매핑
COMPANY_AI_MODELS = {
    "companyA": os.getenv("AI_MODEL_companyA", "gpt-4-turbo"),
    "companyB": os.getenv("AI_MODEL_companyB", "gpt-3.5-turbo"),
    "companyC": os.getenv("AI_MODEL_companyC", "gpt-4-turbo"),
    "companyD": os.getenv("AI_MODEL_companyD", "gpt-3.5-turbo"),
    "companyE": os.getenv("AI_MODEL_companyE", "gpt-3.5-turbo"),
}

# ✅ 모델별 OpenAI API 키 매핑
API_KEYS = {
    "gpt-4-turbo": os.getenv("OPENAI_API_KEY_gpt-4-turbo"),
    "gpt-3.5-turbo": os.getenv("OPENAI_API_KEY_gpt-3.5-turbo"),
}

# ✅ 모든 업체 지원 (한 서버에서 모든 모델을 관리하므로)
ALLOWED_COMPANIES = list(COMPANY_AI_MODELS.keys())

# ✅ 환경 변수 디버깅 출력
print(f"🔍 환경변수 디버그 - DEPLOY_ENV: {DEPLOY_ENV}")
print(f"🔍 환경변수 디버그 - 지원 업체 목록: {ALLOWED_COMPANIES}")
print(f"🔍 환경변수 디버그 - OPENAI_API_KEY_gpt-4-turbo: {'*****' if API_KEYS.get('gpt-4-turbo') else '❌ 없음'}")
print(f"🔍 환경변수 디버그 - OPENAI_API_KEY_gpt-3.5-turbo: {'*****' if API_KEYS.get('gpt-3.5-turbo') else '❌ 없음'}")

def get_company_settings(company_name):
    """특정 업체의 AI 모델과 API 키를 반환"""
    if company_name not in ALLOWED_COMPANIES:
        print(f"❌ [ERROR] '{company_name}'은(는) 현재 서버에서 지원되지 않는 업체입니다!")
        raise ValueError(f"❌ 지원되지 않는 업체입니다: {company_name}")

    ai_model = COMPANY_AI_MODELS.get(company_name)
    openai_api_key = API_KEYS.get(ai_model)
    telegram_bot_token = os.getenv(f"TELEGRAM_BOT_TOKEN_{company_name}")

    print(f"📌 디버깅 - {company_name}: AI_MODEL={ai_model}, API_KEY=*****")

    if not ai_model:
        raise ValueError(f"❌ '{company_name}'의 AI 모델이 설정되지 않았습니다!")
    if not openai_api_key:
        raise ValueError(f"❌ {company_name}의 OpenAI API 키가 설정되지 않았습니다.")

    print(f"✅ {company_name} 설정 로드 완료 - AI_MODEL: {ai_model}, API_KEY: {openai_api_key[:5]}*****")

    return {
        "AI_MODEL": ai_model,
        "OPENAI_API_KEY": openai_api_key,
        "TELEGRAM_BOT_TOKEN": telegram_bot_token
    }

# ✅ 백엔드 URL 설정 (환경 변수 BACKEND_URL이 있으면 해당 값을 사용하고, 없으면 기본값 사용)
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
print(f"🔍 백엔드 URL: {BACKEND_URL}")
