import os
import sys
from langchain_community.document_loaders import (
    DirectoryLoader, TextLoader, CSVLoader, UnstructuredExcelLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from config import OPENAI_API_KEY  # ✅ 환경변수에서 API 키 가져오기

# ✅ 명령어 인자 개수 확인
if len(sys.argv) != 2:
    print("❌ 사용법: python create_vector_db.py [업체명]")
    sys.exit(1)

company_name = sys.argv[1]

# ✅ 업체별 환경변수에서 OpenAI API 키 가져오기
openai_api_key = os.getenv(f"OPENAI_API_KEY_{company_name}")

if not openai_api_key:
    print(f"❌ {company_name}의 OpenAI API 키가 설정되지 않았습니다.")
    sys.exit(1)

# ✅ Loader 선택 함수
def loader_selector(filepath):
    if filepath.endswith('.txt'):
        return TextLoader(filepath, encoding='utf-8')
    elif filepath.endswith('.csv'):
        return CSVLoader(filepath, encoding='utf-8')
    elif filepath.endswith('.xlsx') or filepath.endswith('.xls'):
        return UnstructuredExcelLoader(filepath)
    else:
        raise ValueError(f"지원하지 않는 파일 형식입니다: {filepath}")

# ✅ 벡터DB 경로 설정
company_db_path = f'./database/{company_name}'
faiss_db_path = f'./faiss_indexes/{company_name}_index'

# ✅ 디렉터리가 존재하는지 확인
if not os.path.exists(company_db_path):
    print(f"❌ '{company_db_path}' 폴더가 없습니다. 폴더와 문서를 먼저 추가하세요.")
    sys.exit(1)

try:
    # ✅ 문서 로딩
    print(f"📂 {company_name}의 문서를 로딩 중...")
    loader = DirectoryLoader(company_db_path, glob='**/*.*', loader_cls=loader_selector)
    documents = loader.load()
    
    if not documents:
        print(f"⚠️ {company_name}의 데이터가 비어 있습니다. 벡터DB를 생성하지 않습니다.")
        sys.exit(1)

    # ✅ 문서 쪼개기
    print(f"🔄 문서를 처리 중...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_documents(documents)

    # ✅ 벡터DB 생성 및 저장
    print(f"🛠️ {company_name}의 벡터DB 생성 중...")
    vectorstore = FAISS.from_documents(texts, OpenAIEmbeddings(api_key=openai_api_key))
    vectorstore.save_local(faiss_db_path)

    print(f"✅ {company_name}의 벡터DB 생성 완료! 저장 위치: {faiss_db_path}")

except Exception as e:
    print(f"❌ 벡터DB 생성 중 오류 발생: {str(e)}")
    sys.exit(1)
