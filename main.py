from app.ui.streamlit_app import init_session_state, render_main_ui
from lib.clients.corenest import perform_ping

if __name__ == "__main__":
    perform_ping()
    init_session_state()
    render_main_ui()
