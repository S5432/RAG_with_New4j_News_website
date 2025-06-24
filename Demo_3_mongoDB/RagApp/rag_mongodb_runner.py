# rag_runner.py
# RAG pipeline using FAISS + Local MongoDB with full metadata support

from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from pymongo import MongoClient
import os
import logging
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# MongoDB connection
mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["newsdb"]
collection = db["hip_hop_dx_news_table"]

# Initialize Gemini model and embedding
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2)
embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# Load FAISS vector index
faiss_index = FAISS.load_local("faiss_index", embedding_model, allow_dangerous_deserialization=True)

# Create retriever
retriever = faiss_index.as_retriever(search_type="similarity", search_kwargs={"k": 5})

# Prompt template
prompt_template = PromptTemplate.from_template("""
You are a helpful and factual news assistant. Use the provided articles to answer the question accurately.
If the answer is not contained in the documents, say "I couldn't find that information in the articles."

{context}

Question: {question}

Answer:
""")

# Retrieval QA Chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type="stuff",
    chain_type_kwargs={"prompt": prompt_template},
    return_source_documents=True
)

# Main RAG function
def run_rag_query(query: str, debug: bool = False) -> str:
    logging.info(f"[Query] {query}")
    try:
        result = qa_chain.invoke({"query": query})
        answer = result["result"]

        if debug:
            docs = result["source_documents"]
            debug_info = "\n\n".join([
                f"Title: {doc.metadata.get('title', 'N/A')}\n"
                f"Author: {doc.metadata.get('author', 'N/A')}\n"
                f"Date: {doc.metadata.get('publication_date', 'N/A')}\n"
                f"URL: {doc.metadata.get('url', 'N/A')}\n"
                f"Content Preview: {doc.page_content[:500]}..."
                for doc in docs
            ])
            return f"Answer: {answer}\n\nSources:\n{debug_info}"

        return answer

    except Exception as e:
        logging.error(f"[Error] {e}")
        return f"[Error] {str(e)}"

# Command-line testing
if __name__ == "__main__":
    q = "Who wrote the article titled ‘R. Kelly Hospitalized Following Alleged Overdose In Prison’?"
    print(run_rag_query(q, debug=True))
