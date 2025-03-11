import os
from dotenv import load_dotenv

# ✅ 환경변수 로드
load_dotenv()

# ✅ 환경변수 확인
OPENAI_API_KEY_GPT4 = os.getenv("OPENAI_API_KEY_gpt-4-turbo")
print(f"🔍 OPENAI_API_KEY_gpt-4-turbo: {OPENAI_API_KEY_GPT4}")

if not OPENAI_API_KEY_GPT4:
    raise ValueError("❌ OpenAI API 키가 설정되지 않았습니다. .env 파일을 확인하세요!")

# ✅ 환경변수 확인
print(f"🔍 OPENAI_API_KEY_gpt-4-turbo: {os.getenv('OPENAI_API_KEY_gpt-4-turbo')}")

# ✅ 지원하는 업체 리스트 가져오기
COMPANY_NAMES = os.getenv("COMPANY_NAMES", "").strip().split(",")

print(f"🔍 디버그 - COMPANY_NAMES: {COMPANY_NAMES}")  # ✅ 현재 지원 업체 목록 출력

def get_company_settings(company_name):
    """ 특정 업체의 AI 모델과 API 키, 텔레그램 봇 토큰을 가져옴 """
    if not company_name or company_name not in COMPANY_NAMES:
        raise ValueError(f"❌ '{company_name}'는 이 서버에서 지원되지 않는 업체입니다. 현재 지원 업체: {COMPANY_NAMES}")

    ai_model_key = f"AI_MODEL_{company_name}"  # ✅ 올바른 키 포맷 확인
    ai_model = os.getenv(ai_model_key)
    openai_api_key = os.getenv("OPENAI_API_KEY")
    telegram_bot_token = os.getenv(f"TELEGRAM_BOT_TOKEN_{company_name}")  # 업체별 텔레그램 봇 토큰

    print(f"🔍 디버그 - {company_name}: AI_MODEL={ai_model}, OPENAI_API_KEY={openai_api_key}")

    if not ai_model:
        raise ValueError(f"❌ '{company_name}'의 AI 모델이 설정되지 않았습니다. (환경 변수 키: {ai_model_key})")
    if not openai_api_key:
        raise ValueError(f"❌ OpenAI API 키가 설정되지 않았습니다.")

    return {
        "AI_MODEL": ai_model,
        "OPENAI_API_KEY": openai_api_key,
        "TELEGRAM_BOT_TOKEN": telegram_bot_token
    }


# ✅ 백엔드 URL 설정 (로컬 or 서버 환경 자동 감지)
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")