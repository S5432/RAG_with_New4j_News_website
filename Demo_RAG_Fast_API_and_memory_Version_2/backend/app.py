from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag_chain import run_rag_query, clear_rag_memory

app = FastAPI(
    title="HipHopDX RAG API",
    description="RAG-powered question answering with Neo4j + Gemini + memory",
    version="1.0.0",
)

# Enable CORS for frontend usage (like Streamlit, React, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  #Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class QueryRequest(BaseModel):
    query: str

# Response model
class QueryResponse(BaseModel):
    answer: str


# Main RAG query endpoint
@app.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    result = run_rag_query(request.query)
    return QueryResponse(answer=result)


# Endpoint to clear memory (start new conversation)
@app.post("/clear")
async def clear_memory():
    clear_rag_memory()
    return {"message": "Conversation memory cleared successfully."}


#  Simple health check
@app.get("/")
async def root():
    return {"message": " HipHopDX RAG API is running!"}
