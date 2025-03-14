import time
from chatbot import get_chatbot_response
from config import get_company_settings
from app import get_company_db, ChatHistory

company_name = "companyA"
settings = get_company_settings(company_name)
openai_api_key = settings["OPENAI_API_KEY"]

Session = get_company_db(company_name)

def save_to_db(user_message, bot_response):
    with Session() as session:
        new_chat = ChatHistory(user_message=user_message, bot_response=bot_response)
        session.add(new_chat)
        session.commit()

# 초기 메시지 설정
initial_message = "돈을 벌기 위한 창의적인 사업 아이디어를 하나 제시해줘."
current_message = initial_message

# 대화 횟수 설정 (테스트로 5번 정도가 적당)
conversation_rounds = 5

for i in range(conversation_rounds):
    print(f"[AI-1 질문 {i+1}] {current_message}")
    response_ai_2 = get_chatbot_response(current_message, company_name, settings["AI_MODEL"], openai_api_key)
    print(f"[AI-2 응답 {i+1}] {response_ai_2}")
    save_to_db(current_message, response_ai_2)

    time.sleep(2)  # API 제한 대비 잠시 대기

    # AI-2의 응답을 다시 AI-1의 다음 질문으로 사용
    current_message = response_ai_2
