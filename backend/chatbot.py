import openai
from config import OPENAI_API_KEY

# ✅ OpenAI API 클라이언트 설정
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def get_chatbot_response(user_message):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=100,
            temperature=0.5
        )
        return response.choices[0].message.content.strip()

    except openai.OpenAIError as e:
        return f"❌ OpenAI API 오류 발생: {str(e)}"

    except Exception as e:
        return f"❌ 서버 오류 발생: {str(e)}"
