import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.graphs import Neo4jGraph
from langchain.memory import ConversationBufferMemory,ConversationBufferWindowMemory

# Load environment variables from .env
load_dotenv()

# --- ENV Vars ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# --- Gemini LLM Setup ---
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",
    temperature=0.2
)

# --- Neo4j Graph Setup ---
graph = Neo4jGraph(
    url=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
)

# --- Conversation Memory ---
memory = ConversationBufferWindowMemory(
    k = 7, #  Only keep the last 5 query result
    memory_key="chat_history",
    return_messages=True
)

###################
# memory = ConversationBufferMemory(
#     memory_key="chat_history",
#     input_key="query",
#     return_messages=True
# )

# --- Exported objects ---
__all__ = ["llm", "graph", "memory"]
