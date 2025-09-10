import streamlit as st
import utils.constants as constants
from utils.helpers.qdrant import perform_semantic_search
from utils.helpers.corenest import fetch_embeddings, fetch_llm_response

def _perform_RAG(user_query):
    try:
        embeddings = fetch_embeddings(user_query)
        semantic_search_result = perform_semantic_search(constants.QDRANT_COLLECTION_NAME, embeddings)

        if not semantic_search_result:
            return "I'm sorry, but I could not find any relevant information in my knowledge base to answer your question."

        context = [ point.payload.get('text') for point in semantic_search_result ]
        context = "\n".join(context)
        answer = fetch_llm_response(user_query, context)

        return answer
    except Exception as e:
        st.toast("Failed to generate response. Try after sometime!")

def init_session_state():
    if 'user_query' not in st.session_state:
        st.session_state.user_query = ""

def render_main_ui():
    print('rendering UI...')
    st.title("AI/ML Knowledge Bot")
    st.write("This is a simple RAG (Retrieval-Augmented Generation) system.")
    st.write("You can ask questions related to AI and ML, and the system will provide answers based on its knowledgebase.")
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
        else:
            st.warning("Please enter a query!")
