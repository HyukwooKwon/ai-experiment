import os
import sys
from pathlib import Path
from langchain_community.document_loaders import (
    DirectoryLoader, TextLoader, CSVLoader, UnstructuredExcelLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from config import get_company_settings  # ✅ 환경 변수 불러오기

def get_openai_credentials(company_name):
    """ 특정 업체의 AI 모델과 OpenAI API 키 가져오기 """
    settings = get_company_settings(company_name)
    return settings["AI_MODEL"], settings["OPENAI_API_KEY"]

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

def create_or_update_faiss(company_name):
    """ 특정 업체의 벡터 DB를 생성 또는 업데이트 """
    ai_model, openai_api_key = get_openai_credentials(company_name)

    # ✅ 절대 경로 설정
    base_dir = Path(__file__).resolve().parent
    company_db_path = base_dir / "database" / company_name
    faiss_db_path = base_dir / "faiss_indexes" / f"{company_name}_index"

    print(f"\n🔍 벡터DB 생성 시작 - {company_name}")
    print(f"📂 데이터 경로 확인: {company_db_path.resolve()}")
    
    if not company_db_path.exists():
        print(f"❌ '{company_db_path}' 폴더가 없습니다. 벡터DB를 생성할 수 없습니다.")
        return

    try:
        print(f"📂 {company_name}의 문서를 로딩 중...")
        files = list(company_db_path.glob("*.*"))
        print(f"📌 파일 목록: {files if files else '없음'}")

        if not files:
            print(f"⚠️ {company_name}의 데이터가 비어 있습니다. 벡터DB를 생성하지 않습니다.")
            return

        print(f"🚀 DirectoryLoader 실행 중...")
        loader = DirectoryLoader(str(company_db_path), glob="*.*", loader_cls=loader_selector)
        documents = loader.load()
        print(f"✅ 파일 로드 완료, 문서 개수: {len(documents)}")

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        texts = text_splitter.split_documents(documents)

        print(f"🔄 문서 임베딩 진행 중...")
        vectorstore = FAISS.from_documents(texts, OpenAIEmbeddings(api_key=openai_api_key))
        vectorstore.save_local(str(faiss_db_path))

        print(f"✅ {company_name}의 벡터DB 생성 완료! 저장 위치: {faiss_db_path}\n")

    except Exception as e:
        print(f"❌ 벡터DB 생성 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ 사용법: python create_vector_db.py <company_name>")
        sys.exit(1)

    company_name = sys.argv[1]
    print(f"✅ create_vector_db.py 실행됨. 입력된 업체명: {company_name}")

    create_or_update_faiss(company_name)
