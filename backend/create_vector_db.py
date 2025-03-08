from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
import openai

openai.api_key = "YOUR_OPENAI_API_KEY"

# 1. 문서 불러오기
loader = TextLoader("faq.txt", encoding="utf-8")  # FAQ.txt 파일 필요
documents = loader.load()

# 2. 문서 쪼개기
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
texts = text_splitter.split_documents(documents)

# 3. 벡터DB 저장
vectorstore = FAISS.from_documents(texts, OpenAIEmbeddings())
vectorstore.save_local("faiss_index")  # 저장

print("✅ 벡터DB 생성 완료!")
