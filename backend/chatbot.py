import os
from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader, TextLoader, CSVLoader, UnstructuredExcelLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
import openai
from config import get_company_settings
from database import get_company_db, ChatHistory


def get_faiss_db_path(company_name):
    base_dir = Path(__file__).resolve().parent
    return base_dir / "faiss_indexes" / f"{company_name}_index"


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
    settings = get_company_settings(company_name)
    openai_api_key = settings["OPENAI_API_KEY"]

    if not openai_api_key:
        print(f"❌ {company_name}의 OpenAI API 키가 없습니다! 벡터DB를 생성할 수 없습니다.")
        return

    base_dir = Path(__file__).resolve().parent
    database_dir = base_dir / "database" / company_name
    faiss_db_path = get_faiss_db_path(company_name)

    if not database_dir.exists():
        print(f"❌ '{database_dir}' 폴더가 없습니다. 벡터DB를 생성할 수 없습니다.")
        return

    try:
        loader = DirectoryLoader(str(database_dir), glob='**/*.*', loader_cls=loader_selector, use_multithreading=True)
        documents = loader.load()

        if not documents:
            print(f"⚠️ {company_name}의 데이터가 비어 있습니다.")
            return

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        texts = text_splitter.split_documents(documents)

        vectorstore = FAISS.from_documents(texts, OpenAIEmbeddings(api_key=openai_api_key))
        vectorstore.save_local(str(faiss_db_path))

        print(f"✅ {company_name}의 벡터DB 생성 완료: {faiss_db_path}")

    except Exception as e:
        print(f"❌ 벡터DB 생성 중 오류 발생: {str(e)}")


def load_vectorstore(company_name):
    settings = get_company_settings(company_name)
    openai_api_key = settings["OPENAI_API_KEY"]

    if not openai_api_key:
        print(f"❌ {company_name}의 OpenAI API 키가 없습니다.")
        return None

    faiss_db_path = get_faiss_db_path(company_name)

    if not faiss_db_path.exists():
        create_or_update_faiss(company_name)

    vectorstore = FAISS.load_local(
        str(faiss_db_path),
        OpenAIEmbeddings(api_key=openai_api_key),
        allow_dangerous_deserialization=True
    )
    return vectorstore


def get_chatbot_response(user_message, company_name):
    settings = get_company_settings(company_name)
    Session = get_company_db(settings["DB_PATH"])

    # 최근 5개 대화 불러오기
    with Session() as session:
        recent_chats = session.query(ChatHistory).order_by(ChatHistory.timestamp.desc()).limit(5).all()
        context = "\n\n".join([
            f"질문: {chat.user_message}\n답변: {chat.bot_response}" for chat in recent_chats
        ])

    # 이전 내용을 반드시 참조하도록 프롬프트 강화
    prompt = f"""{settings['PROMPT']} 

이전 대화:
{context}

상대방의 의견:
{user_message}

발전된 아이디어(반드시 이전과 다른 새로운 아이디어):"""

    chat = ChatOpenAI(api_key=settings["OPENAI_API_KEY"], model=settings["AI_MODEL"])
    response = chat.invoke(prompt)

    return getattr(response, 'content', str(response))
