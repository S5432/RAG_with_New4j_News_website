import streamlit as st
from rag_query_runner import run_rag_query  # 🔁 your real backend function

st.title("News RAG Chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask a question about HipHopDX news..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message in UI
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get assistant response using real RAG function
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = run_rag_query(prompt)
            st.markdown(response)

    # Add assistant message to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
