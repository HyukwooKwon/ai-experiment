import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader, CSVLoader, UnstructuredExcelLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
import openai
from config import get_company_settings  # ✅ 수정된 부분

# ✅ 업체별 환경 변수 가져오기 (이제 직접 환경 변수를 사용하지 않음)
def get_openai_credentials(company_name):
    """ 업체별 AI 모델과 OpenAI API 키 가져오기 """
    settings = get_company_settings(company_name)
    return settings["AI_MODEL"], settings["OPENAI_API_KEY"]

# ✅ 벡터DB 경로 동적으로 설정
def get_faiss_db_path(company_name):
    return f"./faiss_indexes/{company_name}_index"

# ✅ 지원하는 파일 유형 로더 선택
def loader_selector(filepath):
    """ 파일 유형별 적절한 로더 선택 """
    if filepath.endswith('.txt'):
        return TextLoader(filepath, encoding='utf-8')
    elif filepath.endswith('.csv'):
        return CSVLoader(filepath, encoding='utf-8')
    elif filepath.endswith('.xlsx') or filepath.endswith('.xls'):
        return UnstructuredExcelLoader(filepath)
    else:
        raise ValueError(f"지원하지 않는 파일 형식입니다: {filepath}")

# ✅ 벡터DB 생성 또는 업데이트
def create_or_update_faiss(company_name):
    """ 특정 업체의 벡터 DB를 생성 또는 업데이트 """
    ai_model, openai_api_key = get_openai_credentials(company_name)

    faiss_db_path = get_faiss_db_path(company_name)
    database_dir = f"./database/{company_name}"

    if not os.path.exists(database_dir):
        print(f"❌ '{database_dir}' 폴더가 없습니다. 벡터DB를 생성할 수 없습니다.")
        return

    try:
        print(f"📂 {company_name}의 문서를 로딩 중...")
        loader = DirectoryLoader(
            database_dir, glob='**/*.*', loader_cls=loader_selector, use_multithreading=True
        )
        documents = loader.load()

        if not documents:
            print(f"⚠️ {company_name}의 데이터가 비어 있습니다. 벡터DB를 생성하지 않습니다.")
            return

        print(f"🔄 문서를 처리 중...")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        texts = text_splitter.split_documents(documents)

        print(f"🛠️ {company_name}의 벡터DB 생성 중...")
        vectorstore = FAISS.from_documents(texts, OpenAIEmbeddings(api_key=openai_api_key))
        vectorstore.save_local(faiss_db_path)

        print(f"✅ {company_name}의 벡터DB 생성 완료! 저장 위치: {faiss_db_path}")

    except Exception as e:
        print(f"❌ 벡터DB 생성 중 오류 발생: {str(e)}")

# ✅ 업체별 vectorstore 로드
def load_vectorstore(company_name):
    """ 특정 업체의 벡터 DB 로드 """
    ai_model, openai_api_key = get_openai_credentials(company_name)

    faiss_db_path = get_faiss_db_path(company_name)
    if not os.path.exists(faiss_db_path):
        create_or_update_faiss(company_name)

    vectorstore = FAISS.load_local(
        faiss_db_path, 
        OpenAIEmbeddings(api_key=openai_api_key), 
        allow_dangerous_deserialization=True
    )
    return vectorstore

# ✅ 챗봇 응답 처리 함수
def get_chatbot_response(user_message, company_name, ai_model, openai_api_key):
    """ 특정 업체의 AI 모델을 사용하여 챗봇 응답 생성 """
    openai.api_key = openai_api_key  # ✅ API 키 설정

    print(f"🚀 {company_name} 업체 요청 - 사용 모델: {ai_model}")

    try:
        chat = ChatOpenAI(api_key=openai_api_key, model=ai_model)
        response = chat.invoke(user_message)

        return response.content if hasattr(response, 'content') else str(response)

    except openai.error.OpenAIError as e:
        return f"❌ OpenAI API 오류 발생: {str(e)}"
    except Exception as e:
        return f"❌ 시스템 오류 발생: {str(e)}"
