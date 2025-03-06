import openai
from config import OPENAI_API_KEY

# ✅ OpenAI API 클라이언트 설정
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def get_chatbot_response(user_message):
    try:
        # ✅ OpenAI GPT-4 API 요청
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 친절한 AI 비서입니다. 사용자에게 도움을 주세요."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=150,
            temperature=0.7
        )

        # ✅ AI 응답 가져오기
        bot_response = response.choices[0].message.content.strip()
        return bot_response

    except openai.OpenAIError as e:
        return f"❌ OpenAI API 오류 발생: {str(e)}"

    except Exception as e:
        return f"❌ 서버 오류 발생: {str(e)}"
