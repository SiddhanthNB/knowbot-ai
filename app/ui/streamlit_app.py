import streamlit as st
from urllib.parse import quote
from app.config.logging import logger
from lib.pipeline.rag import NO_INFO_MESSAGE, perform_rag
from lib.utils.markdown import format_response_for_markdown

def init_session_state():
    if 'user_query' not in st.session_state:
        st.session_state.user_query = ""

def render_main_ui():
    print('rendering UI...')
    st.title("AI/ML Knowledge Bot")
    st.write("This is a simple RAG (Retrieval-Augmented Generation) system.")
    st.write("You can ask questions related to AI and ML, and the system will provide answers based on its knowledge base.")
    st.write("The system uses a combination of semantic search and a language model to generate responses.")
    st.write("Note: The system may take a few seconds to respond based on the complexity of the query.")

    st.divider()

    st.write("Example: What is machine learning?")

    user_input = st.text_input("Enter your query:", "")

    is_disabled = not bool(user_input.strip())

    if st.button("Submit", disabled=is_disabled):
        if user_input.strip():
            with st.spinner("Processing your query..."):
                try:
                    response = perform_rag(user_input)
                except Exception as exc:
                    logger.error(f"Error in perform_rag: {exc}")
                    st.toast("Failed to generate response. Try after sometime!")
                    response = None
            st.session_state.user_query = user_input
            st.markdown(f"**Response:**\n\n{format_response_for_markdown(response)}")

            if response and response != NO_INFO_MESSAGE:
                content_for_chatgpt = f"My original query was: {user_input}\n\nI received this response:\n{response}\n\nCan you please elaborate or provide more details?"
                encoded_content = quote(content_for_chatgpt)
                chatgpt_url = f"https://chat.openai.com/?q={encoded_content}"
                claude_url = f"https://claude.ai/new?q={encoded_content}"

                st.markdown(
                    f"""
                    <div style="display:flex;gap:12px;align-items:center;flex-wrap:wrap;">
                        <a href="{chatgpt_url}" target="_blank">
                            <button style="background-color:#4CAF50;color:white;padding:8px 16px;border:none;border-radius:4px;cursor:pointer;">Continue on ChatGPT</button>
                        </a>
                        <a href="{claude_url}">
                            <button style="background-color:#D97706;color:white;padding:8px 16px;border:none;border-radius:4px;cursor:pointer;">Continue in Claude</button>
                        </a>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.warning("Please enter a query!")
