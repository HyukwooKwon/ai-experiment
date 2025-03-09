import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader, CSVLoader, UnstructuredExcelLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA
import openai
from config import OPENAI_API_KEY  # ✅ config.py에서 API 키 불러오기

openai.api_key = OPENAI_API_KEY

FAISS_DB_PATH = "./faiss_index"
DATABASE_DIR = "./database"

def loader_selector(filepath):
    if filepath.endswith('.txt'):
        return TextLoader(filepath, encoding='utf-8')
    elif filepath.endswith('.csv'):
        return CSVLoader(filepath, encoding='utf-8')
    elif filepath.endswith('.xlsx') or filepath.endswith('.xls'):
        return UnstructuredExcelLoader(filepath)
    else:
        raise ValueError(f"지원하지 않는 파일 형식입니다: {filepath}")

def create_or_update_faiss():
    print("🚨 데이터 변경 감지! 벡터DB를 새로 생성합니다...")
    loader = DirectoryLoader(
        DATABASE_DIR,
        glob='**/*.*',
        loader_cls=loader_selector,
        use_multithreading=True
    )
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_documents(documents)

    vectorstore = FAISS.from_documents(texts, OpenAIEmbeddings(api_key=OPENAI_API_KEY))
    vectorstore.save_local(FAISS_DB_PATH)
    print("✅ 벡터DB 업데이트 완료!")

if not os.path.exists(FAISS_DB_PATH):
    create_or_update_faiss()

vectorstore = FAISS.load_local(
    FAISS_DB_PATH, 
    OpenAIEmbeddings(api_key=OPENAI_API_KEY), 
    allow_dangerous_deserialization=True
)

qa_chain = RetrievalQA.from_chain_type(
    ChatOpenAI(api_key=OPENAI_API_KEY, model='gpt-3.5-turbo'),
    retriever=vectorstore.as_retriever()
)

def get_chatbot_response(user_message):
    try:
        relevant_info = qa_chain.invoke(user_message)['result']
        return relevant_info

    except openai.OpenAIError as e:
        return f"❌ OpenAI API 오류 발생: {str(e)}"

    except Exception as e:
        return f"❌ 오류 발생: {str(e)}"
