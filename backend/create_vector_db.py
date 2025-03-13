import os
import sys
from pathlib import Path
from langchain_community.document_loaders import (
    DirectoryLoader, TextLoader, CSVLoader, UnstructuredExcelLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from config import get_company_settings


def loader_selector(filepath):
    if filepath.endswith('.txt'):
        return TextLoader(filepath, encoding='utf-8')
    elif filepath.endswith('.csv'):
        return CSVLoader(filepath, encoding='utf-8')
    elif filepath.endswith(('.xlsx', '.xls')):
        return UnstructuredExcelLoader(filepath)
    else:
        raise ValueError(f"지원하지 않는 파일 형식입니다: {filepath}")


def create_or_update_faiss(company_name):
    try:
        settings = get_company_settings(company_name)
        openai_api_key = settings["OPENAI_API_KEY"]

        base_dir = Path(__file__).resolve().parent
        database_dir = base_dir / "database" / company_name
        faiss_db_path = base_dir / "faiss_indexes" / f"{company_name}_index"

        if not database_dir.exists():
            print(f"❌ '{database_dir}' 폴더가 없습니다. 벡터DB 생성 실패.")
            return

        print(f"{company_name}의 문서를 로딩 중...")
        loader = DirectoryLoader(str(database_dir), glob='**/*.*', loader_cls=loader_selector, use_multithreading=True)
        documents = loader.load()

        if not documents:
            print(f"{company_name}의 데이터가 비어 있습니다. 벡터DB를 생성하지 않습니다.")
            return

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        texts = text_splitter.split_documents(documents)

        print("문서 임베딩 진행 중...")
        vectorstore = FAISS.from_documents(texts, OpenAIEmbeddings(api_key=openai_api_key))
        faiss_db_path = base_dir / "faiss_indexes" / f"{company_name}_index"
        vectorstore.save_local(str(faiss_db_path))

        print(f"{company_name}의 벡터DB 생성 완료: {faiss_db_path}")

    except Exception as e:
        print(f"벡터DB 생성 중 오류 발생: {str(e)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python create_vector_db.py <company_name>")
        sys.exit(1)

    company_name = sys.argv[1]
    create_or_update_faiss(company_name)
