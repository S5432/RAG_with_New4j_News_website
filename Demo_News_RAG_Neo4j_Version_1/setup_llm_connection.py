######################################################
# This script sets up our Gemini LLM model and Neo4j connection to be reused.
# We have only need to run this once as per app start. it loads the graph + LLM and exposes llm and graph object.
# #####################################################

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.graphs import Neo4jGraph
from dotenv import load_dotenv
import os

# Load the environment variables
load_dotenv()
# Get credentials
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# Initialize Google Gemini LLM
llm = ChatGoogleGenerativeAI(model = "gemini-2.0-flash-lite", temperature = 0.2)


# initialize Neo4j Graph Database connector
graph = Neo4jGraph(
    url = NEO4J_URI,
    username = NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
)

# graph.refresh_schema()

# Exported variables for reuse

__all__ = ["llm", "graph"]