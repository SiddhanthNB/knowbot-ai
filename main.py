from utils.helpers.corenest import perform_ping
from utils.streamlit.gui import init_session_state, render_main_ui

if __name__ == "__main__":
    perform_ping()
    init_session_state()
    render_main_ui()
