import os
from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader, TextLoader, CSVLoader, UnstructuredExcelLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
import openai
from config import get_company_settings


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


def get_chatbot_response(user_message, company_name, ai_model, openai_api_key):
    if not (ai_model and openai_api_key):
        return f"❌ {company_name}의 설정이 잘못되었습니다."

    try:
        vectorstore = load_vectorstore(company_name)

        if vectorstore:
            docs = vectorstore.similarity_search(user_message, k=3)
            context = "\n\n".join(doc.page_content for doc in docs)

            prompt = f"""아래 내용을 참고하여 질문에 답변하세요.\n\n{context}\n\n질문: {user_message}\n답변:"""

            chat = ChatOpenAI(api_key=openai_api_key, model=ai_model)
            response = chat.invoke(prompt)

            return getattr(response, 'content', str(response))
        else:
            return "❌ 벡터DB 로드 실패."

    except openai.error.AuthenticationError:
        return "❌ OpenAI 인증 실패."
    except openai.error.OpenAIError as e:
        print(f"❌ OpenAI API 오류: {str(e)}")
        return f"❌ OpenAI API 오류: {str(e)}"
    except Exception as e:
        print(f"❌ 시스템 오류: {str(e)}")
        return f"❌ 시스템 오류: {str(e)}"
