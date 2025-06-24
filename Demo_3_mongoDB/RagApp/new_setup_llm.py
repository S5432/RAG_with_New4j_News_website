from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
# from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
import os
import pymongo

# Load environment variables
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize LLM and embedding model
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite", temperature=0.2)
embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# MongoDB connection
mongo_client = pymongo.MongoClient("mongodb://localhost:27017")
db = mongo_client["newsdb"]
collection = db["news_data"]  # update this to match your actual collection

# Vector store location (FAISS index)
FAISS_INDEX_PATH = "faiss_index"

# Load or create FAISS index
def load_faiss_index():
    if os.path.exists(FAISS_INDEX_PATH):
        return FAISS.load_local(
            FAISS_INDEX_PATH,
            embeddings=embedding_model,
            allow_dangerous_deserialization=True  # 👈 Explicit permission
        )
    else:
        return FAISS.from_documents([], embedding_model)
# Exported objects
vectorstore = load_faiss_index()

__all__ = ["llm", "embedding_model", "vectorstore", "collection"]
