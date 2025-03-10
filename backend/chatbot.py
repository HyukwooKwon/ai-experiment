import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader, CSVLoader, UnstructuredExcelLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA
import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY
DATABASE_DIR = "./database"

# 벡터DB 경로 동적으로 설정
def get_faiss_db_path(company_name):
    return f"./faiss_indexes/{company_name}_index"

def loader_selector(filepath):
    if filepath.endswith('.txt'):
        return TextLoader(filepath, encoding='utf-8')
    elif filepath.endswith('.csv'):
        return CSVLoader(filepath, encoding='utf-8')
    elif filepath.endswith('.xlsx') or filepath.endswith('.xls'):
        return UnstructuredExcelLoader(filepath)
    else:
        raise ValueError(f"지원하지 않는 파일 형식입니다: {filepath}")

def create_or_update_faiss(company_name):
    faiss_db_path = get_faiss_db_path(company_name)
    database_dir = f"./database/{company_name}"

    loader = DirectoryLoader(
        database_dir,
        glob='**/*.*',
        loader_cls=loader_selector,
        use_multithreading=True
    )
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_documents(documents)

    vectorstore = FAISS.from_documents(texts, OpenAIEmbeddings(api_key=OPENAI_API_KEY))
    vectorstore.save_local(faiss_db_path)
    print(f"✅ {company_name}의 벡터DB 업데이트 완료!")

# 업체별 vectorstore 로드
def load_vectorstore(company_name):
    faiss_db_path = get_faiss_db_path(company_name)
    if not os.path.exists(faiss_db_path):
        create_or_update_faiss(company_name)

    vectorstore = FAISS.load_local(
        faiss_db_path, 
        OpenAIEmbeddings(api_key=OPENAI_API_KEY), 
        allow_dangerous_deserialization=True
    )
    return vectorstore


def get_chatbot_response(user_message, company_name, ai_model, openai_api_key):
    print(f"🚀 {company_name} 업체 요청 - 사용 모델: {ai_model}")  # ✅ 확인용 로그 추가

    try:
        chat = ChatOpenAI(api_key=openai_api_key, model=ai_model)
        response = chat.invoke(user_message)

        # ✅ OpenAI 응답에서 실제 메시지만 추출
        if hasattr(response, 'content'):
            return response.content  # ✅ 올바른 응답 데이터만 반환
        else:
            return str(response)  # 기존과 다르면 문자열로 변환

    except Exception as e:
        return f"❌ OpenAI API 오류 발생: {str(e)}"



