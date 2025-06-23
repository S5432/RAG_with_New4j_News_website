import streamlit as st
import requests

# FastAPI backend endpoint
API_URL = "http://localhost:8000/query"
RESET_URL = "http://localhost:8000/clear"

st.set_page_config(page_title="News RAG Assistant", page_icon="📰")
st.title("📰 HipHopDX News RAG Chatbot")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Sidebar ---
with st.sidebar:
    st.header("Session")
    if st.button("🧹 Clear Conversation"):
        response = requests.post(RESET_URL)
        if response.status_code == 200:
            st.session_state.messages = []
            st.success("Conversation reset!")
        else:
            st.error("Failed to reset memory")

    st.markdown("---")
    st.caption("Powered by FastAPI + LangChain + Gemini + Neo4j")

# --- Display Previous Messages ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- User Input ---
if prompt := st.chat_input("Ask a question about HipHopDX news..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get response from FastAPI backend
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                res = requests.post(API_URL, json={"query": prompt})
                res.raise_for_status()
                answer = res.json()["answer"]  # fixed key
            except Exception as e:
                answer = f"Error: {e}"
            st.markdown(answer)

    # Add assistant message
    st.session_state.messages.append({"role": "assistant", "content": answer})
