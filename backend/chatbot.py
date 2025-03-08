import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_openai import OpenAI
import openai
from config import OPENAI_API_KEY
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

openai.api_key = OPENAI_API_KEY

FAISS_DB_PATH = "faiss_index"
FAQ_FILE = "faq.txt"

# ✅ FAQ 파일이 변경될 때마다 벡터DB를 다시 생성
def create_or_update_faiss():
    print("🚨 FAQ 데이터 변경 감지! 벡터DB를 새로 생성합니다...")
    loader = TextLoader(FAQ_FILE, encoding="utf-8")
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_documents(documents)
    
    # 새롭게 벡터DB 생성
    vectorstore = FAISS.from_documents(texts, OpenAIEmbeddings())
    vectorstore.save_local(FAISS_DB_PATH)
    print("✅ 벡터DB 업데이트 완료!")

# ✅ FAQ 파일이 변경되었거나 벡터DB가 없으면 새로 생성
if not os.path.exists(FAISS_DB_PATH) or os.path.getmtime(FAQ_FILE) > os.path.getmtime(FAISS_DB_PATH):
    create_or_update_faiss()

# ✅ 벡터DB 로드
vectorstore = FAISS.load_local(FAISS_DB_PATH, OpenAIEmbeddings(), allow_dangerous_deserialization=True)
qa_chain = RetrievalQA.from_chain_type(OpenAI(), retriever=vectorstore.as_retriever())

def get_chatbot_response(user_message):
    try:
        relevant_info = qa_chain.invoke(user_message)

        response = openai.Client(api_key=OPENAI_API_KEY).chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 친절한 AI 비서입니다. 사용자에게 도움을 주세요."},
                {"role": "user", "content": f"질문: {user_message}\n\n참고 정보: {relevant_info}"}
            ],
            max_tokens=150,
            temperature=0.7
        )

        return response.choices[0].message.content.strip()

    except openai.OpenAIError as e:
        return f"❌ OpenAI API 오류 발생: {str(e)}"

    except Exception as e:
        return f"❌ 서버 오류 발생: {str(e)}"
