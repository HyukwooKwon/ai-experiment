import os
from dotenv import load_dotenv

# ✅ Render에서도 환경 변수를 올바르게 불러오도록 설정
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

# ✅ 업체별 AI 모델 매핑
COMPANY_AI_MODELS = {
    "companyA": os.getenv("AI_MODEL_companyA"),
    "companyB": os.getenv("AI_MODEL_companyB"),
    "companyC": os.getenv("AI_MODEL_companyC"),
    "companyD": os.getenv("AI_MODEL_companyD"),
}

# ✅ 모델별 OpenAI API 키 매핑
API_KEYS = {
    "gpt-4-turbo": os.getenv("OPENAI_API_KEY_gpt-4-turbo"),
    "gpt-3.5-turbo": os.getenv("OPENAI_API_KEY_gpt-3.5-turbo"),
}

def get_api_key(company: str):
    """업체명으로 올바른 OpenAI API 키를 반환"""
    model = COMPANY_AI_MODELS.get(company)
    if not model:
        raise ValueError(f"❌ {company}의 AI 모델이 설정되지 않았습니다!")

    api_key = API_KEYS.get(model)
    if not api_key:
        raise ValueError(f"❌ {company}({model})의 OpenAI API 키가 설정되지 않았습니다!")

    return api_key


# ✅ 지원하는 업체 리스트 가져오기
COMPANY_NAMES = os.getenv("COMPANY_NAMES", "").strip().split(",")

# ✅ 환경 변수 디버깅 출력
print(f"🔍 환경변수 디버그 - COMPANY_NAMES: {COMPANY_NAMES}")
print(f"🔍 환경변수 디버그 - AI_MODEL_companyA: {COMPANY_AI_MODELS.get('companyA')}")
print(f"🔍 환경변수 디버그 - AI_MODEL_companyB: {COMPANY_AI_MODELS.get('companyB')}")
print(f"🔍 환경변수 디버그 - OPENAI_API_KEY_gpt-4-turbo: {'*****' if API_KEYS.get('gpt-4-turbo') else '❌ 없음'}")
print(f"🔍 환경변수 디버그 - OPENAI_API_KEY_gpt-3.5-turbo: {'*****' if API_KEYS.get('gpt-3.5-turbo') else '❌ 없음'}")

def get_company_settings(company_name):
    """ 특정 업체의 AI 모델과 API 키를 반환 """
    if company_name not in COMPANY_NAMES:
        raise ValueError(f"❌ 지원되지 않는 업체입니다: {company_name}")

    ai_model_key = f"AI_MODEL_{company_name}"  # ✅ AI 모델 키 생성
    ai_model = COMPANY_AI_MODELS.get(company_name)
    openai_api_key = API_KEYS.get(ai_model)  # ✅ 모델별 API 키 매핑
    telegram_bot_token = os.getenv(f"TELEGRAM_BOT_TOKEN_{company_name}")  # 업체별 텔레그램 봇 토큰

    print(f"📌 디버깅 - {company_name}: AI_MODEL={ai_model}, API_KEY=*****")


    if not ai_model:
        raise ValueError(f"❌ '{company_name}'의 AI 모델이 설정되지 않았습니다. (환경 변수 키: {ai_model_key})")
    if not openai_api_key:
        raise ValueError(f"❌ OpenAI API 키가 설정되지 않았습니다.")
    
    print(f"✅ {company_name} 설정 로드 완료 - AI_MODEL: {ai_model}, API_KEY: {openai_api_key[:5]}*****")

    return {
        "AI_MODEL": ai_model,
        "OPENAI_API_KEY": openai_api_key,
        "TELEGRAM_BOT_TOKEN": telegram_bot_token
    }


# ✅ 백엔드 URL 설정 (로컬 or 서버 환경 자동 감지)
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")