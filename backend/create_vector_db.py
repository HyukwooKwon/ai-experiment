from langchain_community.document_loaders import (
    DirectoryLoader, TextLoader, CSVLoader, UnstructuredExcelLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
import openai
import sys
import os

from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

# Loader 선택 함수
def loader_selector(filepath):
    if filepath.endswith('.txt'):
        return TextLoader(filepath, encoding='utf-8')
    elif filepath.endswith('.csv'):
        return CSVLoader(filepath, encoding='utf-8')
    elif filepath.endswith('.xlsx') or filepath.endswith('.xls'):
        return UnstructuredExcelLoader(filepath)
    else:
        raise ValueError(f"지원하지 않는 파일 형식입니다: {filepath}")

# 업체 이름을 명령어로 받도록 수정
if len(sys.argv) != 2:
    print("사용법: python create_vector_db.py [업체명]")
    sys.exit(1)

company_name = sys.argv[1]

# 업체별 디렉토리 경로 설정
company_db_path = f'./database/{company_name}'
faiss_db_path = f'./faiss_indexes/{company_name}_index'

# 디렉터리가 존재하는지 확인
if not os.path.exists(company_db_path):
    print(f"'{company_db_path}' 폴더가 없습니다. 폴더와 문서를 먼저 추가하세요.")
    sys.exit(1)

# 문서 로딩
loader = DirectoryLoader(
    company_db_path,
    glob='**/*.*',
    loader_cls=loader_selector,
    use_multithreading=True
)

documents = loader.load()

# 문서 쪼개기
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
texts = text_splitter.split_documents(documents)

# 벡터DB 생성 및 저장 (업체별)
vectorstore = FAISS.from_documents(texts, OpenAIEmbeddings(api_key=OPENAI_API_KEY))
vectorstore.save_local(faiss_db_path)

print(f"✅ {company_name}의 벡터DB 생성 완료! ({faiss_db_path})")
