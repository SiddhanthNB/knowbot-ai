import streamlit as st
from urllib.parse import quote
import utils.constants as constants
from config.logger import logger
from utils.helpers.qdrant import perform_semantic_search
from utils.helpers.corenest import fetch_embeddings, fetch_llm_response

NO_INFO_MESSAGE = "I'm sorry, but I could not find any relevant information in my knowledge base to answer your question."

def _perform_RAG(user_query):
    try:
        embeddings = fetch_embeddings(user_query)
        semantic_search_result = perform_semantic_search(constants.QDRANT_COLLECTION_NAME, embeddings)

        if not semantic_search_result:
            return NO_INFO_MESSAGE

        context = [ point.payload.get('content', '') for point in semantic_search_result ]
        context = "\n".join(context)

        if not context.strip():
            return NO_INFO_MESSAGE

        answer = fetch_llm_response(user_query, context)

        return answer
    except Exception as e:
        logger.error(f"Error in _perform_RAG: {e}")
        st.toast("Failed to generate response. Try after sometime!")

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
                response = _perform_RAG(user_input)
            st.session_state.user_query = user_input
            st.markdown(f"**Response:**\n\n{response}")

            if response and response != NO_INFO_MESSAGE:
                content_for_chatgpt = f"My original query was: {user_input}\n\nI received this response:\n{response}\n\nCan you please elaborate or provide more details?"
                encoded_content = quote(content_for_chatgpt)
                chatgpt_url = f"https://chat.openai.com/?q={encoded_content}"

                st.markdown(
                    f'<a href="{chatgpt_url}" target="_blank"><button style="background-color:#4CAF50;color:white;padding:8px 16px;border:none;border-radius:4px;cursor:pointer;">Continue on ChatGPT</button></a>',
                    unsafe_allow_html=True
                )
        else:
            st.warning("Please enter a query!")
