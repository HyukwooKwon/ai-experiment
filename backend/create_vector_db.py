from langchain_community.document_loaders import (
    DirectoryLoader, TextLoader, CSVLoader, UnstructuredExcelLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
import openai

openai.api_key = "YOUR_OPENAI_API_KEY"

# 각 확장자에 맞는 Loader를 지정하는 함수 정의
def loader_selector(filepath):
    if filepath.endswith('.txt'):
        return TextLoader(filepath, encoding='utf-8')
    elif filepath.endswith('.csv'):
        return CSVLoader(filepath, encoding='utf-8')
    elif filepath.endswith('.xlsx') or filepath.endswith('.xls'):
        return UnstructuredExcelLoader(filepath)
    else:
        raise ValueError(f"지원하지 않는 파일 형식입니다: {filepath}")

# DirectoryLoader를 사용자 정의 loader로 설정
loader = DirectoryLoader(
    './database',
    glob='**/*.*',
    loader_cls=loader_selector,  # 명시적으로 로더 지정
    use_multithreading=True
)

documents = loader.load()

# 문서 쪼개기
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
texts = text_splitter.split_documents(documents)

# 벡터DB 생성 및 저장
vectorstore = FAISS.from_documents(texts, OpenAIEmbeddings())
vectorstore.save_local("faiss_index")

print("✅ 벡터DB 생성 완료!")
