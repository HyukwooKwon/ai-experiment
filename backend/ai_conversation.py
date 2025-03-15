import time
from chatbot import get_chatbot_response
from database import get_company_db, ChatHistory
from config import get_company_settings

# 두 개의 모델을 명확히 지정
company_name_ai1 = "business"          # GPT-4-turbo
company_name_ai2 = "business_gpt35"    # GPT-3.5-turbo

# DB는 동일
Session = get_company_db(get_company_settings(company_name_ai1)["DB_PATH"])

def save_chat(user_message, bot_response):
    with Session() as session:
        chat = ChatHistory(user_message=user_message, bot_response=bot_response)
        session.add(chat)
        session.commit()

message = "돈을 벌기 위한 창의적인 아이디어를 제시해줘."

for i in range(5):
    # AI-1 (GPT-4-turbo)
    response_ai1 = get_chatbot_response(message, company_name_ai1)
    print(f"[AI-1 (GPT-4) 응답 {i+1}] {response_ai1}")
    save_chat(message, response_ai1)
    time.sleep(3)

    # AI-2 (GPT-3.5-turbo, 비판적인 역할)
    response_ai2 = get_chatbot_response(response_ai1, company_name_ai2)
    print(f"[AI-2 (GPT-3.5) 응답 {i+1}] {response_ai2}")
    save_chat(response_ai1, response_ai2)

    # 다음 질문으로 순환
    message = response_ai2
    time.sleep(3)
