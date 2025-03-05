import os
import openai
import logging
from dotenv import load_dotenv

# ✅ .env 파일 로드
load_dotenv()

# ✅ API 키 로드
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ✅ 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

if not OPENAI_API_KEY:
    logger.error("❌ OpenAI API Key가 설정되지 않았습니다! .env 파일 확인 필요")
    raise ValueError("OpenAI API Key가 설정되지 않았습니다.")
else:
    logger.info(f"🔑 OpenAI API Key 로드 완료: {OPENAI_API_KEY[:5]}*****")

# ✅ OpenAI 클라이언트 초기화 (최신 방식)
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def get_chatbot_response(user_message):
    try:
        logger.info(f"🔹 사용자 메시지: {user_message}")

        # ✅ OpenAI API 요청
        logger.info("🛠 OpenAI API 요청 중...")

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=100,
            temperature=0.5
        )

        # ✅ 응답 데이터 로깅
        logger.info(f"🛠 OpenAI API 응답 원본: {response}")

        # ✅ 최신 OpenAI 응답 형식에 맞춰 데이터 추출
        bot_response = response.choices[0].message.content.strip()
        logger.info(f"💬 챗봇 응답: {bot_response}")

        return bot_response

    except openai.OpenAIError as e:  # ✅ 최신 예외 처리 방식 적용
        logger.error(f"❌ OpenAI API 오류 발생: {str(e)}")
        return "OpenAI API 오류 발생"

    except Exception as e:
        logger.error(f"❌ 일반 오류 발생: {str(e)}", exc_info=True)
        return f"서버 오류 발생: {str(e)}"  # ✅ 오류 메시지 포함하여 반환

# ✅ 테스트 실행
if __name__ == "__main__":
    user_message = "안녕하세요"
    response = get_chatbot_response(user_message)
    print(f"챗봇 응답: {response}")
