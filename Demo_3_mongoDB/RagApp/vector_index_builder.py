from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from dotenv import load_dotenv
import pymongo
import os

# Load environment variables
load_dotenv()

# Initialize embedding model
embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# Connect to MongoDB
mongo_client = pymongo.MongoClient("mongodb://localhost:27017")
db = mongo_client["newsdb"]
collection = db["news_data"]  #  Use your correct collection name here

# Load documents and include full metadata in content
documents = []
for doc in collection.find({}, {
    "title": 1, "author": 1, "description": 1, "full_text": 1,
    "publication_date": 1, "source_url": 1
}):
    title = doc.get("title", "").strip()
    author = doc.get("author", "").strip()
    description = doc.get("description", "").strip()
    full_text = doc.get("full_text", "").strip()
    pub_date = doc.get("publication_date", "").strip()
    url = doc.get("source_url", "").strip()

    # Combine all fields into a searchable string
    combined_content = f"Title: {title}\nAuthor: {author}\nDate: {pub_date}\nURL: {url}\n\n{description}\n\n{full_text}"

    if not combined_content.strip():
        continue  # skip invalid/empty

    metadata = {
        "title": title,
        "author": author,
        "publication_date": pub_date,
        "url": url
    }

    documents.append(Document(page_content=combined_content, metadata=metadata))

print(f" Loaded {len(documents)} non-empty documents from MongoDB.")

if not documents:
    print(" No valid documents found. Exiting.")
    exit()

# Split text into chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
split_docs = splitter.split_documents(documents)
print(f"Split into {len(split_docs)} text chunks.")

# Build and save FAISS index
vectorstore = FAISS.from_documents(split_docs, embedding_model)
vectorstore.save_local("faiss_index")
print("FAISS vector index created and saved successfully.")
