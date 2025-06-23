from setup_llm_connection import llm, graph, memory
from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Refresh schema from Neo4j
graph.refresh_schema()
llm.temperature = 0.2

# Cypher generation prompt
cypher_prompt = PromptTemplate.from_template("""
    You are an expert at translating natural language into Cypher queries for a news database.
    Here is the conversation so far:
    {chat_history}
    Use this schema to answer the user's question:
    {schema}

    Instructions:
    - Articles are represented as nodes with label `Article`, and they have properties like `title`, `description`, `full_text`, and `publication_date`.
    - If the user asks about a person, check if their name appears in any of these fields: `title`, `description`, or `full_text` using `CONTAINS`.
    - If the user asks for a specific year like "from 2025", filter articles where `publication_date.year = 2025`.
    - If the user gives multiple names (e.g., "Kanye West or Jay-Z"), return articles that mention **either** of them using `OR`.
    - If user says "this article" or "it", refer to the most recently discussed article.
    - If there are multiple candidates, ask the user to clarify.

    Example 1:
    Question: Show me articles about Kendrick Lamar from 2025.
    Cypher:
        MATCH (a:Article)
        WHERE (
            a.title CONTAINS "Kendrick Lamar" OR 
            a.description CONTAINS "Kendrick Lamar" OR 
            a.full_text CONTAINS "Kendrick Lamar"
        ) AND a.publication_date.year = 2025
        RETURN a
            
    Example 2: 
        Use this schema:
        - (Author)-[:WROTE]->(Article)
        - Article(title, description, publication_date, section)

        If a question is about award show stories, filter articles where the `title` or `description` contains keywords like "award", "grammy", "BET", "MTV", "trophy", "honor".

    Example 3:
    Question: Give the three most recent stories by London Jennn, then count how many of hers were published in the same week.
    Cypher:
        MATCH (a:Article)<-[:WROTE]-(auth:Author)
        WHERE auth.name = "London Jennn"
        WITH a, date.truncate('week', a.publication_date) AS week
        ORDER BY a.publication_date DESC
        WITH collect(a)[0..3] AS recent_articles, week
        UNWIND recent_articles AS article
        RETURN article.title, week, size(recent_articles) AS articles_in_week

    Notes:
    - To count articles per week, use WITH and aggregation, not window functions.
    - Do NOT use OVER, PARTITION BY, or any SQL window function syntax.
    - Do NOT use SHOW ALL PROPERTIES or any SHOW commands.
    - Only use Cypher syntax supported by Neo4j 5.x (or your version).
    - If you need to count articles per week, use aggregation with WITH and RETURN, not window functions.
    - Neo4j Cypher does not support `date.week`. To group or compare by week, use `date.truncate('week', <date>)`.
    - Use `date.truncate('week', a.publication_date)` when you want to compare or group articles by week.
                                                
    Now write the Cypher query for this:

    Question:
    {question}

    Cypher query:
    """)

# QA answer prompt
qa_prompt = PromptTemplate.from_template("""
    You are a helpful assistant. Based on the Cypher result below, answer the user's question clearly.

    Question: {question}
    Result: {context}

    Answer:
    """)

# GraphCypherQAChain (core RAG logic)
cypher_chain = GraphCypherQAChain.from_llm(
    llm=llm,
    graph=graph,
    cypher_prompt=cypher_prompt,
    qa_prompt=qa_prompt,
    verbose=True,
    memory=memory,
    return_intermediate_steps=False,
    allow_dangerous_requests=True,
)

# Fallback memory chat chain (if no Cypher is applicable)
fallback_prompt = PromptTemplate.from_template("""
Continue the conversation based on context.

Chat History:
{chat_history}

User: {query}
AI:""")

fallback_chain = LLMChain(llm=llm, prompt=fallback_prompt, memory=memory)


# Unified function with Cypher → fallback
def run_rag_query(query: str) -> str:
    logging.info(f"[] User query: {query}")
    try:
        result = cypher_chain.invoke({"query": query})
        return result["result"]
    except Exception as e:
        logging.warning(f"[Fallback] Cypher error: {e}")
        return fallback_chain.invoke({"query": query})


#  Clear conversation memory
def clear_rag_memory():
    memory.clear()
    logging.info(" Memory cleared.")
